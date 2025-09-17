import React from 'react';
import styled from 'styled-components';
import { Link, useNavigate } from 'react-router-dom';

type Role = 'patient' | 'clinician';

interface Props {
  loggedIn?: boolean;

  role?: Role;
  onRoleChange?: (r: Role) => void;

  showRoleToggle?: boolean;
}

const Bar = styled.header`
  position: sticky; top: 0; z-index: 40;
  background: #fff; border-bottom: 1px solid #eef0f3;
`;
const Inner = styled.div`
  max-width: 1320px;
  margin: 0 auto;
  padding: 20px 28px;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  @media (max-width: 720px){ grid-template-columns: 1fr; row-gap: 10px; }
`;

const Left = styled.div`display:flex; align-items:center; gap:10px;`;
const Center = styled.div`display:flex; justify-content:center;`;
const Right = styled.div`display:flex; justify-content:flex-end; gap:10px;`;

const Brand = styled(Link)`
  font-weight: 800;
  font-size: 22px;                    
  color: #0d4ecf;
  text-decoration: none;
  display: flex; align-items: center; gap: 10px;
`;

const Pill = styled.div`
  display:flex; padding:4px; border:1px solid #e5e7eb; border-radius:999px;
  background:#f8fafc; gap:4px;
`;

const PillBtn = styled.button<{active?: boolean}>`
  border: none; cursor: pointer;
  border-radius: 999px;
  padding: 8px 14px;                  /* ↑ a bit taller/wider */
  font-weight: 600; font-size: 0.95rem;
  background: ${p=>p.active ? '#111827' : 'transparent'};
  color: ${p=>p.active ? '#fff' : '#111827'};
`;

const HeaderBtn = styled.button`
  border: none; cursor: pointer;
  border-radius: 14px;
  padding: 12px 16px;                 /* ↑ */
  font-weight: 700; font-size: 0.95rem; letter-spacing: .01em;
  background: #0d4ecf; color: #fff;
  &:hover{ filter: brightness(.95); }
`;

const GhostBtn = styled.button`
  border:1px solid #e5e7eb; background:#fff; color:#111827; cursor:pointer;
  border-radius:12px; padding:10px 14px; font-weight:700;
  &:hover{ background:#f8fafc; }
`;

export default function Navbar({ loggedIn, role, onRoleChange, showRoleToggle }: Props) {
  const navigate = useNavigate();

  const effectiveRole: Role =
    role ??
    ((localStorage.getItem('role') as Role) || 'patient');

  const setRole = (r: Role) => {
    localStorage.setItem('role', r);
    onRoleChange?.(r);
  };

  const showToggle = Boolean(onRoleChange || showRoleToggle);

  const CTAs = effectiveRole === 'patient'
    ? (
      <>
        <GhostBtn onClick={() => navigate('/profile')}>My Reports</GhostBtn>
        <HeaderBtn onClick={() => navigate('/diagnosis')}>Start Diagnosis →</HeaderBtn>
      </>
    )
    : (
      <>
        <GhostBtn onClick={() => navigate('/patients')}>Patients</GhostBtn>
        <HeaderBtn onClick={() => navigate('/dashboard')}>Open Dashboard →</HeaderBtn>
      </>
    );

  return (
    <Bar>
      <Inner>
        <Left>
          <Brand to="/">🏥 MediSage</Brand>
        </Left>

        <Center>
          {showToggle && (
            <Pill>
              <PillBtn active={effectiveRole==='patient'} onClick={()=>setRole('patient')}>🧑 Patient</PillBtn>
              <PillBtn active={effectiveRole==='clinician'} onClick={()=>setRole('clinician')}>👨‍⚕️ Clinician</PillBtn>
            </Pill>
          )}
        </Center>

        <Right>
          {CTAs}
        </Right>
      </Inner>
    </Bar>
  );
}
