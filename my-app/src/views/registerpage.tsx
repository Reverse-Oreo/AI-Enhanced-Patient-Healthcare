import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';
import { Button } from 'components/common/Button';
import { Input } from 'components/common/Input';
import type { Role } from 'types/auth';

const RegisterPageWrapper = styled.div<{ $accent: string }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 4rem;

  &:before {
    content: "";
    display: block;
    width: 100%;
    height: 4px;
    background: ${({ $accent }) => $accent};
    position: absolute;
    top: 64px;
    left: 0;
  }
`;

const FormContainer = styled.div`
  max-width: 520px;
  width: 100%;
  margin: 2rem auto;
  padding: 2rem;
  box-shadow: 0 8px 28px rgba(16, 24, 40, 0.08);
  border-radius: 12px;
  background: #fff;
`;

const Title = styled.h2<{ $accent: string }>`
  text-align: center;
  margin: 0 0 1.25rem;
  letter-spacing: -0.02em;
  span { color: ${({ $accent }) => $accent}; }
`;

const ErrorText = styled.p`
  color: #ef4444;
  font-size: 0.9rem;
  text-align: center;
  margin: 0 0 0.75rem;
`;

const SuccessText = styled.p`
  color: #22c55e;
  font-size: 0.9rem;
  text-align: center;
  margin: 0 0 0.75rem;
`;

const Row = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 1rem;
  background: #fff;
`;

const Label = styled.label`
  font-weight: 600;
  margin-bottom: 0.5rem;
  display: block;
`;

const Hint = styled.p`
  text-align: center;
  margin-top: 1rem;
  font-size: 0.95rem;
`;

const StyledLink = styled(Link)`
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
  &:hover { text-decoration: underline; }
`;

const InviteInfo = styled.div`
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
`;

const genderOptions = ['', 'Male', 'Female', 'Prefer not to say'] as const;

const ACCENT: Record<Role, string> = {
  patient:   '#22c55e',
  clinician: '#2563eb', 
  nurse:     '#a855f7',
};

function getViewRole(): Role {
  const saved = localStorage.getItem('viewRole') as Role | null;
  return saved === 'clinician' || saved === 'nurse' ? saved : 'patient';
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const qs = new URLSearchParams(location.search);
  const inviteToken = qs.get('token');
  const intendedRole = (qs.get('role') as Role) || getViewRole();
  const accent = ACCENT[intendedRole];

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [inviteValid, setInviteValid] = useState<boolean | null>(null);
  const [inviteInfo, setInviteInfo] = useState<any>(null);

  // Validate invitation token on mount for clinician/nurse registration
  useEffect(() => {
    const validateInvite = async () => {
      if ((intendedRole === 'clinician' || intendedRole === 'nurse') && inviteToken) {
        try {
          const response = await fetch(`/api/validate-invitation?token=${inviteToken}`);
          const data = await response.json();
          
          if (data.valid) {
            setInviteValid(true);
            setInviteInfo(data);
            setEmail(data.email); // Pre-fill email from invitation
          } else {
            setInviteValid(false);
            setError('Invalid or expired invitation link.');
          }
        } catch (err) {
          setInviteValid(false);
          setError('Failed to validate invitation.');
        }
      } else if (intendedRole === 'clinician' || intendedRole === 'nurse') {
        // No token provided for restricted role
        setInviteValid(false);
        setError('Registration for medical staff requires a valid invitation.');
      }
    };

    validateInvite();
  }, [intendedRole, inviteToken]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Basic validation
    if (!name || !email || !password || !confirmPassword) {
      setError('Please fill in all required fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Age validation for patients
    if (intendedRole === 'patient') {
      if (!age || !gender) {
        setError('Age and gender are required for patient registration');
        return;
      }
      const nAge = Number(age);
      if (!Number.isFinite(nAge) || nAge < 1 || nAge > 120) {
        setError('Please enter a valid age between 1 and 120');
        return;
      }
    }

    // Invitation validation for medical staff
    if ((intendedRole === 'clinician' || intendedRole === 'nurse')) {
      if (!inviteToken || !inviteValid) {
        setError('Valid invitation required for medical staff registration');
        return;
      }
    }

    setLoading(true);

    try {
      const payload: any = {
        name,
        email,
        password,
        role: intendedRole,
      };

      if (intendedRole === 'patient') {
        payload.age = Number(age);
        payload.gender = gender;
      }

      if (inviteToken) {
        payload.invitationToken = inviteToken;
      }

      const response = await fetch(`/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Registration failed');
      }

      // Navigate to confirmation pending or success page
      navigate('/confirmation-pending', {
        state: {
          registrationData: payload,
          message: data.message
        },
        replace: true,
      });

    } catch (error) {
      console.error('Registration error:', error);
      setError(error instanceof Error ? error.message : 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Show error for invalid invitations
  if ((intendedRole === 'clinician' || intendedRole === 'nurse') && inviteValid === false) {
    return (
      <>
        <Navbar />
        <RegisterPageWrapper $accent={accent}>
          <FormContainer>
            <Title $accent={accent}>Registration Not Available</Title>
            <ErrorText>
              {error || 'This registration link is invalid or has expired.'}
            </ErrorText>
            <Hint>
              Please contact your administrator for a new invitation link.{' '}
              <StyledLink to="/">Return to homepage</StyledLink>
            </Hint>
          </FormContainer>
        </RegisterPageWrapper>
      </>
    );
  }

  const roleLabel = intendedRole === 'clinician' ? 'Clinician'
    : intendedRole === 'nurse' ? 'Nurse'
    : 'Patient';

  return (
    <>
      <Navbar />
      <RegisterPageWrapper $accent={accent}>
        <FormContainer>
          <Title $accent={accent}>
            {roleLabel} <span>Sign up</span>
          </Title>

          {/* Show invitation info for medical staff */}
          {inviteValid && inviteInfo && (
            <InviteInfo>
              <strong>Invitation Details:</strong><br />
              Role: {inviteInfo.role}<br />
              Invited by: {inviteInfo.inviterName}
            </InviteInfo>
          )}

          {error && <ErrorText>{error}</ErrorText>}

          <form onSubmit={handleSubmit}>
            <Input 
              type="text" 
              value={name} 
              onChange={setName} 
              placeholder="Full Name" 
              disabled={loading} 
            />

            <Input
              type="email"
              value={email}
              onChange={setEmail}
              placeholder="Email"
              disabled={loading || (inviteValid && inviteInfo)}
              style={{ marginTop: '1rem' }}
            />

            {/* Show age/gender only for patients */}
            {intendedRole === 'patient' && (
              <Row>
                <div style={{ flex: 1 }}>
                  <Label htmlFor="age">Age</Label>
                  <Input
                    id="age"
                    type="number"
                    value={age}
                    onChange={(v) => {
                      if (v === '' || (/^\d+$/.test(v) && +v >= 1 && +v <= 120)) setAge(v);
                    }}
                    min={1}
                    max={120}
                    placeholder="Enter your age"
                    disabled={loading}
                  />
                </div>

                <div style={{ flex: 1 }}>
                  <Label htmlFor="gender">Gender</Label>
                  <Select
                    id="gender"
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    disabled={loading}
                  >
                    {genderOptions.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt || 'Select gender'}
                      </option>
                    ))}
                  </Select>
                </div>
              </Row>
            )}

            <Input
              type="password"
              value={password}
              onChange={setPassword}
              placeholder="Password"
              disabled={loading}
              style={{ marginTop: '1rem' }}
            />
            <Input
              type="password"
              value={confirmPassword}
              onChange={setConfirmPassword}
              placeholder="Confirm password"
              disabled={loading}
              style={{ marginTop: '1rem' }}
            />

            <Button
              type="submit"
              disabled={loading || (intendedRole !== 'patient' && !inviteValid)}
              variant="primary"
              style={{ width: '100%', marginTop: '1.25rem' }}
            >
              {loading ? 'Creating account...' : 'Create account'}
            </Button>
          </form>

          <Hint>
            Already have an account?{' '}
            <StyledLink to={`/login?role=${intendedRole}`}>Log in</StyledLink>
          </Hint>
        </FormContainer>
      </RegisterPageWrapper>
    </>
  );
}