import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import Navbar from 'components/homepage/Navbar';
import { useAuth } from 'contexts/AuthContext';
import { AuthService } from 'services/auth';

type Role = 'patient' | 'clinician' | 'nurse';

const SuccessText = styled.div`
  color: #22c55e; 
  font-size: 13px; 
  text-align: center; 
  margin: 0 0 8px;
`;

const ErrorText = styled.div`
  color: #ef4444; 
  font-size: 13px; 
  text-align: center; 
  margin: 0 0 8px;
`;

const Page = styled.div<{ $accent: string }>`
  display:flex; justify-content:center; padding:96px 16px 40px;
  &:before { content:""; position:fixed; top:64px; left:0; right:0; height:4px; background:${p=>p.$accent}; }
`;
const Card = styled.form`
  width:100%; max-width:420px; background:#fff; border-radius:12px;
  box-shadow:0 8px 28px rgba(16,24,40,.08); padding:24px;
`;
const Title = styled.h2<{ $accent: string }>`
  margin:0 0 8px; text-align:center; letter-spacing:-.02em;
  span{ color:${p=>p.$accent}; }
`;
const Input = styled.input`
  width:100%; padding:12px 14px; border-radius:10px; border:1px solid #e5e7eb;
  font-size:14px; outline:none; transition:border .15s;
  &:focus{ border-color:#9db7ff; }
  & + & { margin-top:12px; }
`;
const Button = styled.button<{ $variant?: 'primary' | 'ghost' }>`
  margin-top:14px; width:100%; padding:10px 14px; border-radius:10px; font-weight:700;
  border:0; cursor:pointer;
  background:${p=>p.$variant==='ghost'?'#f6f7fb':'#1365ff'};
  color:${p=>p.$variant==='ghost'?'#222':'#fff'};
`;
const Error = styled.div`color:#ef4444; font-size:13px; text-align:center; margin:0 0 8px;`;

// ✅ Parse role from the query string (supports nurse)
function getRoleFromSearch(search: string, fallback: Role = 'patient'): Role {
  const r = new URLSearchParams(search).get('role')?.toLowerCase();
  return r === 'patient' || r === 'clinician' || r === 'nurse' ? (r as Role) : fallback;
}

const ACCENT: Record<Role, string> = {
  patient: '#22c55e',
  clinician: '#2563eb',
  nurse: '#8b5cf6',
};

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const params = new URLSearchParams(location.search);
  const confirmed = params.get('confirmed');
  const error = params.get('error');

  const intendedRole = getRoleFromSearch(location.search);
  const next = new URLSearchParams(location.search).get('next') || '';
  const accent = ACCENT[intendedRole];

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [err, setErr] = useState<string|null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null); setLoading(true);
    try {
      // Update the AuthService.login call to include role
      await AuthService.login({ email, password, role: intendedRole });
      await login(); // refresh context/user

      const defaultDest =
        intendedRole === 'clinician' ? '/clinician-home' :
        intendedRole === 'nurse'     ? '/nurse-home' :
                                      '/patient-home';

      navigate(next || defaultDest, { replace: true });
    } catch (e: any) {
      setErr(e?.message ?? 'Failed to log in.');
    } finally {
      setLoading(false);
    }
  };
  
  const roleLabel =
    intendedRole === 'clinician' ? 'Clinician' :
    intendedRole === 'nurse'     ? 'Nurse' :
                                   'Patient';

  return (
    <>
      <Navbar />
      <Page $accent={accent}>
        <Card onSubmit={onSubmit}>
          <Title $accent={accent}>{roleLabel} <span>Login</span></Title>
          
          {/* Move the confirmation messages here */}
          {confirmed && <SuccessText>Email confirmed! You can now log in.</SuccessText>}
          {error === 'confirmation_failed' && <ErrorText>Email confirmation failed. Please try again.</ErrorText>}
          
          {err && <Error>{err}</Error>}

          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={e=>setEmail(e.target.value)}
            disabled={loading}
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e=>setPassword(e.target.value)}
            disabled={loading}
          />

          <Button disabled={loading}>{loading ? 'Logging in…' : 'Log in'}</Button>
        </Card>
      </Page>
    </>
  );
}
