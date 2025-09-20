export type Role = 'patient' | 'clinician';

const isTrue = (v?: string) => String(v ?? '').toLowerCase() === 'true';

// Bypass is allowed only in non-production builds
export const BYPASS =
  isTrue(process.env.REACT_APP_BYPASS_AUTH) &&
  process.env.NODE_ENV !== 'production';

// what role to impersonate during bypass
const rawRole = (process.env.REACT_APP_BYPASS_ROLE ?? '').toLowerCase();
export const BYPASS_ROLE: Role | undefined =
  rawRole === 'patient' || rawRole === 'clinician' ? (rawRole as Role) : undefined;
