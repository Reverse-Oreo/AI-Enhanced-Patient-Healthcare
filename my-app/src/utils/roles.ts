export type Role = 'patient' | 'clinician' | 'nurse' ;

const KEY = 'view-role';

export const getViewRole = (): Role =>
  ((localStorage.getItem(KEY) as Role) || 'patient');

export const setViewRole = (r: Role) => {
  localStorage.setItem(KEY, r);
};
