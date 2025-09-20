// src/components/homepage/Navbar.tsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from 'contexts/AuthContext';
import { BYPASS } from 'utils/bypass';

type Role = 'patient' | 'clinician';

const VIEW_ROLE_KEY = 'medisage:viewRole';

function getViewRole(): Role {
  try {
    const v = localStorage.getItem(VIEW_ROLE_KEY) as Role | null;
    return v === 'clinician' ? 'clinician' : 'patient';
  } catch {
    return 'patient';
  }
}
function setViewRole(r: Role) {
  try {
    localStorage.setItem(VIEW_ROLE_KEY, r);
  } catch {}
}
/* ----------------------------------------------------------------- */

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  // UI toggle role (used only when not logged in)
  const [viewRole, setViewRoleState] = React.useState<Role>(getViewRole());
  const changeRole = (r: Role) => {
    setViewRole(r);
    setViewRoleState(r);
  };

  // Considered authenticated 
  const authed = Boolean(user) || BYPASS;

  const effectiveRole: Role =
    (user?.role as Role | undefined) ?? viewRole;

  const loginHref = `/login?as=${viewRole}&next=${encodeURIComponent(
    location.pathname + location.search,
  )}`;
  const signupHref = `/register?as=${viewRole}`;

  return (
    <Bar>
      <Left>
        <Brand to="/">
          <Logo aria-hidden="true">🧑‍⚕️</Logo>
          <span>MediSage</span>
        </Brand>
      </Left>

      <Center>
        <Pill>
          <PillBtn
            $active={viewRole === 'patient' || effectiveRole === 'patient'}
            onClick={() => changeRole('patient')}
            disabled={Boolean(user)} // lock when real role is present
            type="button"
          >
            🧑‍⚕️ Patient
          </PillBtn>
          <PillBtn
            $active={viewRole === 'clinician' || effectiveRole === 'clinician'}
            onClick={() => changeRole('clinician')}
            disabled={Boolean(user)}
            type="button"
          >
            👩‍⚕️ Clinician
          </PillBtn>
        </Pill>
      </Center>

      <Right>
        {authed ? (
          effectiveRole === 'patient' ? (
            <>
              <Ghost to="/profile">My Reports</Ghost>
              <Primary to="/diagnosis">Start Diagnosis →</Primary>
              {user && (
                <Tiny onClick={logout} type="button" title="Log out">
                  Log out
                </Tiny>
              )}
            </>
          ) : (
            <>
              <Ghost to="/patients">Patients</Ghost>
              <Primary to="/clinician">Open Dashboard →</Primary>
              {user && (
                <Tiny onClick={logout} type="button" title="Log out">
                  Log out
                </Tiny>
              )}
            </>
          )
        ) : (
          <>
            <Ghost to={loginHref}>Log in</Ghost>
            <Primary to={signupHref}>Sign up</Primary>
          </>
        )}
      </Right>
    </Bar>
  );
};

export default Navbar;

/* ======================= styled bits ======================= */
const Bar = styled.header`
  position: sticky;
  top: 0;
  z-index: 20;
  background: #fff;
  border-bottom: 1px solid rgba(0,0,0,0.06);
  height: 64px;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 0 20px;
`;

const Left = styled.div`
  display: flex;
  align-items: center;
`;
const Center = styled.div`
  display: flex;
  justify-content: center;
`;
const Right = styled.nav`
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  align-items: center;
`;

const Brand = styled(Link)`
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 20px;
  color: #1365ff;
  text-decoration: none;
`;
const Logo = styled.span`
  font-size: 22px;
`;

const Pill = styled.div`
  display: inline-flex;
  background: #f3f5f9;
  border-radius: 999px;
  padding: 4px;
  gap: 4px;
`;
const PillBtn = styled.button<{ $active?: boolean }>`
  border: 0;
  background: ${({ $active }) => ($active ? '#fff' : 'transparent')};
  color: ${({ $active }) => ($active ? '#111' : '#444')};
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 999px;
  box-shadow: ${({ $active }) =>
    $active ? '0 1px 2px rgba(0,0,0,0.08)' : 'none'};
  cursor: pointer;
  opacity: ${({ disabled }) => (disabled ? 0.7 : 1)};
`;

const BaseBtn = styled(Link)`
  text-decoration: none;
  font-weight: 600;
  border-radius: 10px;
  padding: 8px 14px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
`;
const Primary = styled(BaseBtn)`
  background: #1365ff;
  color: #fff;
  box-shadow: 0 6px 14px rgba(19, 101, 255, 0.2);
`;
const Ghost = styled(BaseBtn)`
  background: #f6f7fb;
  color: #222;
`;
const Tiny = styled.button`
  background: transparent;
  border: 0;
  color: #6b7280;
  font-size: 12px;
  padding: 6px 8px;
  cursor: pointer;
`;
