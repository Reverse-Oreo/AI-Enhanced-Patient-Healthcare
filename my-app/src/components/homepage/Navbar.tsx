import { Link, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from 'contexts/AuthContext';
import type { Role } from 'types/auth';

// public home per role
const homeByRole: Record<Role, string> = {
  patient: '/patient-home',
  clinician: '/clinician-home',
  nurse: '/nurse-home',
};

/* ========== UI ========== */
const Bar = styled.header`
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 10px 16px;
  background: #fff;
  border-bottom: 1px solid rgba(0,0,0,.06);
`;

const Left = styled.div`
  justify-self: start;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const Center = styled.div`
  justify-self: center;
`;

const Right = styled.div`
  justify-self: end;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const Brand = styled(Link)`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  text-decoration: none;
  color: #111;
`;

const ToggleGroup = styled.div`
  display: flex;
  gap: 8px;
  background: #f5f6f7;
  padding: 4px;
  border-radius: 999px;
`;

const Toggle = styled.button<{active: boolean}>`
  padding: 6px 12px;
  border: 0;
  border-radius: 999px;
  cursor: pointer;
  background: ${p => (p.active ? '#fff' : 'transparent')};
  box-shadow: ${p => (p.active ? '0 1px 2px rgba(0,0,0,.08)' : 'none')};
  font-weight: 600;
`;

const CTA = styled(Link)<{primary?: boolean}>`
  padding: 8px 12px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  background: ${p => (p.primary ? '#1f6bff' : '#f2f3f5')};
  color: ${p => (p.primary ? '#fff' : '#111')};
`;

const GhostBtn = styled.button`
  background: transparent;
  border: 0;
  cursor: pointer;
  font-weight: 600;
  color: #111;
`;

/* ========== Component ========== */
const roleLabel = (r: Role) => {
  if (r === 'clinician') return 'Doctor';
  return r[0].toUpperCase() + r.slice(1);
};

export default function Navbar() {
  const { user, logout, viewRole, setViewRoleState } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const loggedIn = !!user;

  // Brand goes to the user’s home when logged in; otherwise general homepage
  const brandHref = loggedIn ? homeByRole[user!.role] : '/';

  // Auth links should reflect the *previewed* role
  const toLogin  = (role: Role) =>
    `/login?role=${role}&next=${encodeURIComponent(location.pathname + location.search)}`;
  const toSignup = (role: Role) => `/register?role=${role}`;

  // When you switch the preview role, also navigate to that role’s public home
  const handlePreview = (role: Role) => {
    setViewRoleState(role);
    navigate(homeByRole[role], { replace: true });
  };

  return (
    <Bar>
      <Left>
        <Brand to={brandHref}>
          <span role="img" aria-label="doc">🧑‍⚕️</span>
          <span>MediSage</span>
        </Brand>
      </Left>

      <Center>
        <ToggleGroup aria-label="preview role">
          {(['patient', 'clinician', 'nurse'] as Role[]).map((r) => (
            <Toggle
              key={r}
              active={viewRole === r}
              onClick={() => handlePreview(r)}
              aria-pressed={viewRole === r}
            >
              {roleLabel(r)}
            </Toggle>
          ))}
        </ToggleGroup>
      </Center>

      <Right>
        {loggedIn ? (
          <GhostBtn
            onClick={async () => {
              await logout();
              navigate('/', { replace: true });
            }}
          >
            Log out
          </GhostBtn>
        ) : (
          <>
            <CTA to={toLogin(viewRole)}>Log in</CTA>
            <CTA to={toSignup(viewRole)} primary>Sign up</CTA>
          </>
        )}
      </Right>
    </Bar>
  );
}
