import React, { useState, useEffect } from 'react';
import { useAuth } from 'contexts/AuthContext';

const AdminInvite = () => {
  const { user } = useAuth();
  
  const [invitations, setInvitations] = useState([
    // Mock data for demonstration
    {
      id: '1',
      email: 'nurse@example.com',
      role: 'nurse',
      token: 'abc123',
      created_at: '2024-01-15T10:00:00Z',
      expires_at: '2024-01-22T10:00:00Z',
      used_at: null
    },
    {
      id: '2', 
      email: 'doctor@example.com',
      role: 'clinician',
      token: 'def456',
      created_at: '2024-01-10T10:00:00Z',
      expires_at: '2024-01-17T10:00:00Z',
      used_at: '2024-01-12T14:30:00Z'
    }
  ]);
  
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    role: 'nurse'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Check if user has permission to manage invitations
  //const canManageInvitations = user?.role === 'clinician' || user?.role === 'admin';
const canManageInvitations = true; //bypass for now

  useEffect(() => {
    if (canManageInvitations) {
      fetchInvitations();
    }
  }, [canManageInvitations]);

  const fetchInvitations = async () => {
    try {
      const response = await fetch('http://localhost:8000/auth/admin/invitations', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setInvitations(data);
      }
    } catch (err) {
      console.error('Failed to fetch invitations:', err);
    }
  };

  const sendInvitation = async (e: React.MouseEvent<HTMLButtonElement>) => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('http://localhost:8000/auth/admin/send-invitation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData),
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(`Invitation sent successfully to ${formData.email}`);
        setFormData({ email: '', role: 'nurse' });
        setShowForm(false);
        fetchInvitations();
      } else {
        setError(data.detail || 'Failed to send invitation');
      }
    } catch (err) {
      setError('Failed to send invitation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const revokeInvitation = async (invitationId: string) => {
    if (!window.confirm('Are you sure you want to revoke this invitation?')) return;

    try {
      // Mock API call - replace with your actual API
      console.log('Revoking invitation:', invitationId);
      
      // Update the invitation in local state
      setInvitations(prev => prev.map(inv => 
        inv.id === invitationId 
          ? { ...inv, expires_at: new Date().toISOString() }
          : inv
      ));
      
      setSuccess('Invitation revoked successfully');
      
    } catch (err) {
      setError('Failed to revoke invitation');
    }
  };

  const getStatusBadge = (invitation: any) => {
    if (invitation.used_at) {
      return <span style={{background: '#d1fae5', color: '#065f46', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.875rem', fontWeight: '600'}}>Used</span>;
    }
    if (new Date(invitation.expires_at) < new Date()) {
      return <span style={{background: '#fee2e2', color: '#991b1b', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.875rem', fontWeight: '600'}}>Expired</span>;
    }
    return <span style={{background: '#fef3c7', color: '#92400e', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.875rem', fontWeight: '600'}}>Pending</span>;
  };

  if (!canManageInvitations) {
    return (
      <div style={{maxWidth: '1200px', margin: '0 auto', padding: '2rem'}}>
        <div style={{background: '#fee2e2', color: '#991b1b', padding: '1rem', borderRadius: '8px', border: '1px solid #fca5a5'}}>
          You don't have permission to access this page.
        </div>
      </div>
    );
  }

  return (
    <div style={{maxWidth: '1200px', margin: '0 auto', padding: '2rem'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
        <h1 style={{margin: 0, color: '#1f2937'}}>Staff Invitation Management</h1>
        <button 
          style={{background: '#3b82f6', color: 'white', border: 'none', padding: '0.75rem 1.5rem', borderRadius: '8px', fontWeight: '600', cursor: 'pointer'}}
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : 'Send New Invitation'}
        </button>
      </div>

      {error && <div style={{background: '#fee2e2', color: '#991b1b', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', border: '1px solid #fca5a5'}}>{error}</div>}
      {success && <div style={{background: '#d1fae5', color: '#065f46', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', border: '1px solid #a7f3d0'}}>{success}</div>}

      {showForm && (
        <div style={{background: '#fff', borderRadius: '12px', padding: '2rem', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', marginBottom: '2rem'}}>
          <h3 style={{margin: '0 0 1.5rem 0', color: '#1f2937'}}>Send Staff Invitation</h3>
          <div>
            <div style={{marginBottom: '1.5rem'}}>
              <label style={{display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#374151'}}>Email Address</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                placeholder="Enter staff member's email"
                required
                disabled={loading}
                style={{width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '1rem'}}
              />
            </div>

            <div style={{marginBottom: '1.5rem'}}>
              <label style={{display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#374151'}}>Role</label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
                disabled={loading}
                style={{width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '1rem'}}
              >
                <option value="nurse">Nurse</option>
                <option value="clinician">Doctor</option>
              </select>
            </div>

            <div style={{display: 'flex', gap: '1rem'}}>
              <button 
                type="button" 
                onClick={sendInvitation}
                disabled={loading}
                style={{background: '#3b82f6', color: 'white', border: 'none', padding: '0.75rem 1.5rem', borderRadius: '8px', fontWeight: '600', cursor: 'pointer'}}
              >
                {loading ? 'Sending...' : 'Send Invitation'}
              </button>
              <button 
                type="button"
                onClick={() => setShowForm(false)}
                disabled={loading}
                style={{background: '#f3f4f6', color: '#374151', border: '1px solid #d1d5db', padding: '0.75rem 1.5rem', borderRadius: '8px', fontWeight: '600', cursor: 'pointer'}}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div style={{background: '#fff', borderRadius: '12px', padding: '2rem', boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'}}>
        <h3 style={{margin: '0 0 1.5rem 0', color: '#1f2937'}}>Invitation History</h3>
        
        {invitations.length === 0 ? (
          <div style={{textAlign: 'center', padding: '3rem', color: '#6b7280'}}>
            <p>No invitations sent yet.</p>
          </div>
        ) : (
          <div style={{overflowX: 'auto'}}>
            <table style={{width: '100%', borderCollapse: 'collapse'}}>
              <thead>
                <tr>
                  <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #e5e7eb', background: '#f9fafb', fontWeight: '600', color: '#374151'}}>Email</th>
                  <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #e5e7eb', background: '#f9fafb', fontWeight: '600', color: '#374151'}}>Role</th>
                  <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #e5e7eb', background: '#f9fafb', fontWeight: '600', color: '#374151'}}>Status</th>
                  <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #e5e7eb', background: '#f9fafb', fontWeight: '600', color: '#374151'}}>Sent Date</th>
                  <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #e5e7eb', background: '#f9fafb', fontWeight: '600', color: '#374151'}}>Expires</th>
                  <th style={{padding: '1rem', textAlign: 'left', borderBottom: '1px solid #e5e7eb', background: '#f9fafb', fontWeight: '600', color: '#374151'}}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {invitations.map((invitation) => (
                  <tr key={invitation.id}>
                    <td style={{padding: '1rem', borderBottom: '1px solid #e5e7eb'}}>{invitation.email}</td>
                    <td style={{padding: '1rem', borderBottom: '1px solid #e5e7eb'}}>
                      <span style={{background: invitation.role === 'nurse' ? '#ede9fe' : '#dbeafe', color: invitation.role === 'nurse' ? '#7c3aed' : '#2563eb', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.875rem', fontWeight: '600'}}>
                        {invitation.role}
                      </span>
                    </td>
                    <td style={{padding: '1rem', borderBottom: '1px solid #e5e7eb'}}>{getStatusBadge(invitation)}</td>
                    <td style={{padding: '1rem', borderBottom: '1px solid #e5e7eb'}}>{new Date(invitation.created_at).toLocaleDateString()}</td>
                    <td style={{padding: '1rem', borderBottom: '1px solid #e5e7eb'}}>{new Date(invitation.expires_at).toLocaleDateString()}</td>
                    <td style={{padding: '1rem', borderBottom: '1px solid #e5e7eb'}}>
                      {!invitation.used_at && new Date(invitation.expires_at) > new Date() && (
                        <div>
                          <button
                            style={{background: '#f3f4f6', color: '#374151', border: '1px solid #d1d5db', padding: '0.5rem 1rem', fontSize: '0.875rem', marginRight: '0.5rem', borderRadius: '6px', cursor: 'pointer'}}
                            onClick={() => {
                              const inviteUrl = `${window.location.origin}/register?token=${invitation.token}&role=${invitation.role}`;
                              navigator.clipboard.writeText(inviteUrl);
                              setSuccess('Invitation link copied to clipboard');
                              setTimeout(() => setSuccess(''), 3000);
                            }}
                          >
                            Copy Link
                          </button>
                          <button
                            style={{background: '#ef4444', color: 'white', border: 'none', padding: '0.5rem 1rem', fontSize: '0.875rem', borderRadius: '6px', cursor: 'pointer'}}
                            onClick={() => revokeInvitation(invitation.id)}
                          >
                            Revoke
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminInvite;