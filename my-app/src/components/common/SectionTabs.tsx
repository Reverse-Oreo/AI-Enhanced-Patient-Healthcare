import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const Bar = styled.div`
  border-bottom: 1px solid #eef0f3;
  background: #fff;
`;
const Wrap = styled.div`
  max-width: 1320px;
  margin: 0 auto;
  padding: 8px 16px;
  display: flex;
  gap: 8px;
  align-items: center;
`;
const Tab = styled(Link)<{ $active?: boolean }>`
  padding: 8px 12px;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
  border: 1px solid ${({ $active }) => ($active ? '#2563eb' : '#e5e7eb')};
  color: ${({ $active }) => ($active ? '#2563eb' : '#374151')};
  background: ${({ $active }) => ($active ? '#eff6ff' : '#fff')};
  &:hover { border-color: #c7d2fe; }
`;

function isAny(pathname: string, patterns: RegExp[]) {
  return patterns.some(rx => rx.test(pathname));
}

export default function SectionTabs() {
  const { pathname } = useLocation();

  // Decide which set to show based on route
  const inPatient =
    isAny(pathname, [/^\/$/, /^\/home/, /^\/diagnosis/, /^\/profile/, /^\/reports/]);

  const inClinician =
    isAny(pathname, [/^\/patients(\/.*)?$/, /^\/patient\/.+/, /^\/clinicianDashboard/]);

  const inNurse =
    isAny(pathname, [/^\/nurse-patients(\/.*)?$/, /^\/nurse-worklist/]);

  if (!inPatient && !inClinician && !inNurse) return null;

  let items: Array<{ to: string; label: string; active: boolean }> = [];

  if (inPatient) {
    items = [
      { to: '/diagnosis', label: 'Start Diagnosis', active: pathname.startsWith('/diagnosis') },
      { to: '/profile',   label: 'My Reports',     active: pathname.startsWith('/profile') || pathname.startsWith('/reports') },
    ];
  } else if (inClinician) {
    items = [
      { to: '/patients',            label: 'Patients',  active: pathname.startsWith('/patients') || pathname.startsWith('/patient/') },
      { to: '/clinicianDashboard',  label: 'Dashboard', active: pathname.startsWith('/clinicianDashboard') },
    ];
  } else if (inNurse) {
    items = [
      { to: '/nurse-patients',  label: 'Patients', active: pathname.startsWith('/nurse-patients') },
      { to: '/nurse-worklist',  label: 'Worklist', active: pathname.startsWith('/nurse-worklist') },
    ];
  }

  return (
    <Bar>
      <Wrap>
        {items.map(it => (
          <Tab key={it.to} to={it.to} $active={it.active}>
            {it.label}
          </Tab>
        ))}
      </Wrap>
    </Bar>
  );
}
