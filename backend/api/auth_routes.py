import os
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Form
from supabase import create_client, Client
from pydantic import BaseModel, EmailStr
import jwt
from datetime import datetime, timedelta
from typing import Optional
import json
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import BackgroundTasks

# --- Configuration & Setup ---
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Supabase Client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_API_KEY")
supabase: Client = create_client(url, key)

# JWT Secret for cookies
JWT_SECRET = os.getenv("JWT_SECRET")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL")

# --- Pydantic Models ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: str
    gender: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    age: str
    gender: str

class InvitationCreate(BaseModel):
    email: EmailStr
    role: str  # 'clinician' or 'nurse'

class RegistrationWithInvite(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    invitation_token: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    
medical_report_node = None

def get_medical_report_node():
    """Get or create medical report node with loaded adapter"""
    global medical_report_node
    if medical_report_node is None:
        from managers.model_manager import model_manager
        adapter = model_manager.get_local_adapter()
        if adapter is None:
            raise HTTPException(status_code=503, detail="Models not loaded yet")
        medical_report_node = MedicalReportNode(adapter, supabase)
    return medical_report_node

# --- Helper Functions ---
def set_auth_cookie(response: Response, user_data: dict):
    """Set auth cookie with user data embedded including role"""
    to_encode = {
        "sub": str(user_data["id"]),
        "email": user_data["email"],
        "name": user_data.get("name", ""),
        "age": user_data.get("age", ""),
        "gender": user_data.get("gender", ""),
        "role": user_data.get("role", "patient"),
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    response.set_cookie(
        key="access_token",
        value=encoded_jwt,
        httponly=True,
        samesite="lax",
        secure=False
    )

def get_current_user(request: Request):
    """Get user data directly from JWT cookie including role"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            return None
            
        return {
            "id": user_id,
            "email": payload.get("email", ""),
            "name": payload.get("name", ""),
            "age": payload.get("age", ""),
            "gender": payload.get("gender", ""),
            "role": payload.get("role", "patient")
        }
    except (jwt.PyJWTError, Exception) as e:
        print(f"JWT decode error: {e}")
        return None

async def send_invitation_email_with_password(email: str, token: str, role: str, inviter_name: str, password: str):
    """Send invitation email with temporary password"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = f"Invitation to Join MediSage as {role.title()}"
        
        invite_url = f"{FRONTEND_URL}/register?token={token}&role={role}"
        
        body = f"""
        Dear Healthcare Professional,
        
        You have been invited by {inviter_name} to join MediSage as a {role.title()}.
        
        Your account has been created with the following credentials:
        Email: {email}
        Temporary Password: {password}
        
        Please login using these credentials and change your password immediately.
        Login URL: {FRONTEND_URL}/login
        
        This invitation will expire in 7 days.
        
        Best regards,
        The MediSage Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# --- API Endpoints ---
@router.post("/register")
async def register_user(user_data: UserCreate, response: Response, role: str = "patient"):
    try:
        print(f"🔐 Registration attempt for: {user_data.email} as {role}")
        
        if not url or not key:
            raise HTTPException(status_code=500, detail="Server configuration error")
        
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "name": user_data.name,
                    "age": user_data.age,
                    "gender": user_data.gender,
                    "role": role
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Failed to create user account")
        
        # Determine which table to use based on role
        profile_table = "user_profiles"
        if role == "clinician":
            profile_table = "doctor_profile"
        elif role == "nurse":
            profile_table = "nurse_profile"
        
        # Create user profile
        profile_data = {
            "id": auth_response.user.id,
            "name": user_data.name,
            "age": user_data.age,
            "gender": user_data.gender
        }
        
        profile_result = supabase.table(profile_table).upsert(profile_data).execute()
        
        if not profile_result.data:
            raise HTTPException(status_code=500, detail="Failed to create user profile")
        
        return {
            "message": "User registered successfully",
            "user_id": auth_response.user.id,
            "email_confirmation_required": True,
            "email": user_data.email,
            "role": role
        }
        
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@router.post("/login")
async def login_user(user_data: UserLogin, response: Response, role: str = "patient"):
    try:
        user_session = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if not user_session.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Check user's role from metadata
        user_role = user_session.user.user_metadata.get("role", "patient")
        if user_role != role:
            raise HTTPException(status_code=403, detail=f"User is not a {role}")

        # Determine which table to use based on role
        profile_table = "user_profiles"
        if role == "clinician":
            profile_table = "doctor_profile"
        elif role == "nurse":
            profile_table = "nurse_profile"

        try:
            profile_result = supabase.table(profile_table)\
                .select("*")\
                .eq("id", user_session.user.id)\
                .execute()
            
            if profile_result.data:
                profile = profile_result.data[0]
                user_cookie_data = {
                    "id": user_session.user.id,
                    "email": user_session.user.email,
                    "name": profile.get("name", ""),
                    "age": profile.get("age", ""),
                    "gender": profile.get("gender", ""),
                    "role": role
                }
            else:
                user_cookie_data = {
                    "id": user_session.user.id,
                    "email": user_session.user.email,
                    "name": user_session.user.user_metadata.get("name", ""),
                    "age": user_session.user.user_metadata.get("age", ""),
                    "gender": user_session.user.user_metadata.get("gender", ""),
                    "role": role
                }
                
                # Create missing profile
                try:
                    profile_data = {
                        "id": user_session.user.id,
                        "name": user_cookie_data["name"],
                        "age": user_cookie_data["age"],
                        "gender": user_cookie_data["gender"]
                    }
                    supabase.table(profile_table).upsert(profile_data).execute()
                    print(f"✅ Created missing {role} profile for {user_session.user.email}")
                except Exception as e:
                    print(f"⚠️ Failed to create missing profile: {e}")
                    
        except Exception as e:
            print(f"⚠️ Failed to fetch {role} profile: {e}")
            user_cookie_data = {
                "id": user_session.user.id,
                "email": user_session.user.email,
                "name": user_session.user.user_metadata.get("name", ""),
                "age": user_session.user.user_metadata.get("age", ""),
                "gender": user_session.user.user_metadata.get("gender", ""),
                "role": role
            }
        
        set_auth_cookie(response, user_cookie_data)
        
        return {
            "message": "Login successful", 
            "user": user_cookie_data
        }
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    request: Request,
    response: Response
):
    """Allow users to change their password"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # First verify current password
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": user["email"],
                "password": password_data.current_password
            })
        except:
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password using admin API
        update_response = supabase.auth.admin.update_user_by_id(
            user["id"],
            {"password": password_data.new_password}
        )
        
        # Update user metadata to remove temp password flag
        current_metadata = update_response.user.user_metadata or {}
        if "temp_password" in current_metadata:
            new_metadata = {**current_metadata, "temp_password": False}
            supabase.auth.admin.update_user_by_id(
                user["id"],
                {"user_metadata": new_metadata}
            )
        
        # Refresh the auth cookie
        set_auth_cookie(response, user)
        
        return {"message": "Password updated successfully"}
        
    except Exception as e:
        print(f"Password change error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update password")

@router.get("/password-status")
async def get_password_status(request: Request):
    """Check if user needs to change their temporary password"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Get user metadata to check if they have a temporary password
        auth_user = supabase.auth.admin.get_user_by_id(user["id"])
        needs_password_change = auth_user.user.user_metadata.get("temp_password", False)
        
        return {"needs_password_change": needs_password_change}
    except:
        return {"needs_password_change": False}

@router.post("/admin/send-invitation")
async def send_invitation(
    invitation: InvitationCreate,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Send an invitation to a new staff member and create their account"""
    
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if invitation.role not in ['clinician', 'nurse']:
        raise HTTPException(status_code=400, detail="Invalid role specified")
    
    # Check if user already exists
    try:
        # Check in auth users
        auth_users = supabase.auth.admin.list_users()
        existing_auth_user = next((u for u in auth_users if u.email == invitation.email), None)
        if existing_auth_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
    except Exception as e:
        print(f"User check error: {e}")
    
    # Generate secure token and random password
    token = secrets.token_urlsafe(32)
    random_password = secrets.token_urlsafe(12)
    
    try:
        # Create user in Supabase Auth with random password
        auth_response = supabase.auth.admin.create_user({
            "email": invitation.email,
            "password": random_password,
            "email_confirm": True,
            "user_metadata": {
                "role": invitation.role,
                "name": "Staff Member",
                "temp_password": True
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=500, detail="Failed to create user account")
        
        # Determine which table to use based on role
        profile_table = "doctor_profile" if invitation.role == "clinician" else "nurse_profile"
        
        # Create user profile
        profile_data = {
            "id": auth_response.user.id,
            "name": "Staff Member",
            "age": "",
            "gender": ""
        }
        
        profile_result = supabase.table(profile_table).upsert(profile_data).execute()
        
        if not profile_result.data:
            # Rollback: delete the auth user if profile creation fails
            try:
                supabase.auth.admin.delete_user(auth_response.user.id)
            except:
                pass
            raise HTTPException(status_code=500, detail="Failed to create user profile")
    
    except Exception as e:
        print(f"User creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
    
    # Create invitation record
    invitation_data = {
        'email': invitation.email,
        'role': invitation.role,
        'token': token,
        'invited_by': current_user['id'],
        'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat(),
        'created_at': datetime.utcnow().isoformat()
    }
    
    result = supabase.table('invitations').insert(invitation_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create invitation")
    
    # Send email in background with the random password
    background_tasks.add_task(
        send_invitation_email_with_password,
        invitation.email,
        token,
        invitation.role,
        current_user.get('name', 'Administrator'),
        random_password
    )
    
    return {
        "message": "Invitation sent successfully and user account created",
        "invitation_id": result.data[0]['id'],
        "user_id": auth_response.user.id
    }

@router.get("/admin/invitations")
async def get_invitations(request: Request):
    """Get all invitations"""
    
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = supabase.table('invitations').select('*').order('created_at', desc=True).execute()
    
    return result.data

@router.get("/validate-invitation")
async def validate_invitation(token: str):
    """Validate an invitation token"""
    
    result = supabase.table('invitations').select('*').eq('token', token).execute()
    
    if not result.data:
        return {"valid": False, "message": "Invalid invitation token"}
    
    invitation = result.data[0]
    
    if invitation['used_at']:
        return {"valid": False, "message": "Invitation has already been used"}
    
    if datetime.fromisoformat(invitation['expires_at'].replace('Z', '+00:00')) < datetime.utcnow():
        return {"valid": False, "message": "Invitation has expired"}
    
    return {
        "valid": True,
        "email": invitation['email'],
        "role": invitation['role'],
        "inviterName": "Administrator"
    }

# --- Other endpoints (logout, profile, medical reports, etc.) ---
@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}

@router.get("/profile")
async def get_session(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    user_role = user.get("role", "patient")
    profile_table = "user_profiles"
    
    if user_role == "clinician":
        profile_table = "doctor_profile"
    elif user_role == "nurse":
        profile_table = "nurse_profile"
    
    try:
        profile_result = supabase.table(profile_table)\
            .select("*")\
            .eq("id", user["id"])\
            .execute()
        
        if profile_result.data:
            profile = profile_result.data[0]
            return {
                "id": user["id"],
                "email": user["email"],
                "name": profile.get("name", ""),
                "age": profile.get("age", ""),
                "gender": profile.get("gender", ""),
                "role": user_role
            }
        else:
            return user
            
    except Exception as e:
        print(f"⚠️ Failed to fetch profile from {profile_table}: {e}")
        return user

# ... (other endpoints like update_profile, medical reports, etc. remain the same)