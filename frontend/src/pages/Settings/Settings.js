import React, { useState, useEffect } from 'react';
import { useCompany } from '../../contexts/CompanyContext';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import DeleteCompanyModal from '../../components/Company/DeleteCompanyModal';
import {
  Building2, Users, Plug, Bell, Globe, Save, Plus, Trash2,
  CheckCircle, AlertCircle
} from 'lucide-react';

const Settings = () => {
  const { selectedCompany } = useCompany();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('company');
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Company profile state
  const [companyProfile, setCompanyProfile] = useState({
    name: '',
    industry: '',
    financial_year_start: 1,
    currency: 'USD',
    gst_number: ''
  });

  // User preferences state
  const [preferences, setPreferences] = useState({
    email_alerts: {
      risk_changes: true,
      credit_alerts: true,
      reports: true,
      uploads: true
    },
    notification_frequency: 'immediate',
    language: 'en',
    timezone: 'UTC',
    date_format: 'YYYY-MM-DD',
    currency_display: 'symbol',
    default_dashboard_view: 'overview'
  });

  // Integrations state
  const [integrations, setIntegrations] = useState([]);
  const [showIntegrationForm, setShowIntegrationForm] = useState(false);
  const [newIntegration, setNewIntegration] = useState({
    integration_type: '',
    provider_name: '',
    api_endpoint: '',
    sync_frequency: 'daily',
    is_active: false
  });

  // User management state
  const [users, setUsers] = useState([]);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [newUser, setNewUser] = useState({
    email: '',
    role: 'viewer',
    first_name: '',
    last_name: ''
  });

  // Fetch data
  useEffect(() => {
    if (selectedCompany) {
      fetchCompanyProfile();
      fetchUserPreferences();
      fetchIntegrations();
      fetchUsers();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCompany]);

  const fetchCompanyProfile = async () => {
    try {
      const response = await axios.get('/api/settings/company');
      setCompanyProfile(response.data);
    } catch (err) {
      console.error('Failed to fetch company profile:', err);
    }
  };

  const fetchUserPreferences = async () => {
    try {
      const response = await axios.get('/api/settings/preferences');
      setPreferences(response.data);
    } catch (err) {
      console.error('Failed to fetch user preferences:', err);
    }
  };

  const fetchIntegrations = async () => {
    try {
      const response = await axios.get('/api/settings/integrations');
      setIntegrations(response.data.integrations || []);
    } catch (err) {
      console.error('Failed to fetch integrations:', err);
    }
  };

  const fetchUsers = async () => {
    try {
      // Mock data for now - implement actual user management API
      setUsers([
        { id: '1', email: user?.email || 'admin@company.com', role: 'admin', status: 'active' }
      ]);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    }
  };

  const saveCompanyProfile = async () => {
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.put('/api/settings/company', companyProfile);
      setCompanyProfile(response.data);
      setSuccess('Company profile updated successfully!');

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to update company profile');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const saveUserPreferences = async () => {
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.put('/api/settings/preferences', preferences);
      setPreferences(response.data);
      setSuccess('Preferences updated successfully!');

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to update preferences');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const createIntegration = async () => {
    setSaving(true);
    setError('');

    try {
      const response = await axios.post('/api/settings/integrations', newIntegration);
      setIntegrations([...integrations, response.data]);
      setShowIntegrationForm(false);
      setNewIntegration({
        integration_type: '',
        provider_name: '',
        api_endpoint: '',
        sync_frequency: 'daily',
        is_active: false
      });
      setSuccess('Integration added successfully!');

      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to add integration');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const inviteUser = async () => {
    setSaving(true);
    setError('');

    try {
      await axios.post('/api/settings/users/invite', newUser);
      setShowInviteForm(false);
      setNewUser({
        email: '',
        role: 'viewer',
        first_name: '',
        last_name: ''
      });
      setSuccess('Invitation sent successfully!');

      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to send invitation');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'company', label: 'Company Profile', icon: Building2 },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'integrations', label: 'Integrations', icon: Plug },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'localization', label: 'Language & Localization', icon: Globe }
  ];

  if (!selectedCompany) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">Please select a company to view settings</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Manage company, users, integrations, and preferences</p>
      </div>

      {/* Success/Error Messages */}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <CheckCircle className="h-5 w-5 text-green-400" />
            <div className="ml-3">
              <p className="text-sm text-green-800">{success}</p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              <div className="flex items-center space-x-2">
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </div>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {/* Company Profile Tab */}
        {activeTab === 'company' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium text-gray-900">Company Profile</h3>
              <button
                onClick={() => setShowDeleteModal(true)}
                className="inline-flex items-center px-3 py-1.5 border border-red-300 rounded-md text-sm font-medium text-red-700 bg-red-50 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                <Trash2 className="h-4 w-4 mr-1.5" />
                Delete Company
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Company Name</label>
                <input
                  type="text"
                  value={companyProfile.name}
                  onChange={(e) => setCompanyProfile({ ...companyProfile, name: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Industry</label>
                <select
                  value={companyProfile.industry}
                  onChange={(e) => setCompanyProfile({ ...companyProfile, industry: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="">Select Industry</option>
                  <option value="technology">Technology</option>
                  <option value="manufacturing">Manufacturing</option>
                  <option value="retail">Retail</option>
                  <option value="services">Services</option>
                  <option value="general">General</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Financial Year Start</label>
                <select
                  value={companyProfile.financial_year_start}
                  onChange={(e) => setCompanyProfile({ ...companyProfile, financial_year_start: parseInt(e.target.value) })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value={1}>January</option>
                  <option value={2}>February</option>
                  <option value={3}>March</option>
                  <option value={4}>April</option>
                  <option value={5}>May</option>
                  <option value={6}>June</option>
                  <option value={7}>July</option>
                  <option value={8}>August</option>
                  <option value={9}>September</option>
                  <option value={10}>October</option>
                  <option value={11}>November</option>
                  <option value={12}>December</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
                <select
                  value={companyProfile.currency}
                  onChange={(e) => setCompanyProfile({ ...companyProfile, currency: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="INR">INR (₹)</option>
                  <option value="JPY">JPY (¥)</option>
                  <option value="CAD">CAD ($)</option>
                  <option value="AUD">AUD ($)</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">GST Number</label>
                <input
                  type="text"
                  value={companyProfile.gst_number}
                  onChange={(e) => setCompanyProfile({ ...companyProfile, gst_number: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={saveCompanyProfile}
                disabled={saving}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
              >
                <Save className="h-4 w-4 mr-2" />
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        )}

        {/* User Management Tab */}
        {activeTab === 'users' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-medium text-gray-900">User Management</h3>
              <button
                onClick={() => setShowInviteForm(true)}
                className="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-primary-600 bg-primary-50 hover:bg-primary-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <Plus className="h-4 w-4 mr-2" />
                Invite User
              </button>
            </div>

            {/* Invite Form */}
            {showInviteForm && (
              <div className="mb-6 p-4 border border-gray-200 rounded-lg">
                <h4 className="text-md font-medium text-gray-900 mb-4">Invite New User</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input
                      type="email"
                      value={newUser.email}
                      onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
                    <select
                      value={newUser.role}
                      onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    >
                      <option value="admin">Admin</option>
                      <option value="finance_manager">Finance Manager</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                    <input
                      type="text"
                      value={newUser.first_name}
                      onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                    <input
                      type="text"
                      value={newUser.last_name}
                      onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    />
                  </div>
                </div>
                <div className="mt-4 flex justify-end space-x-3">
                  <button
                    onClick={() => setShowInviteForm(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={inviteUser}
                    disabled={saving}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                  >
                    {saving ? 'Sending...' : 'Send Invitation'}
                  </button>
                </div>
              </div>
            )}

            {/* Users List */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{user.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          {user.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button className="text-red-600 hover:text-red-900">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Integrations Tab */}
        {activeTab === 'integrations' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-medium text-gray-900">Integrations</h3>
              <button
                onClick={() => setShowIntegrationForm(true)}
                className="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-primary-600 bg-primary-50 hover:bg-primary-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Integration
              </button>
            </div>

            {/* Integration Form */}
            {showIntegrationForm && (
              <div className="mb-6 p-4 border border-gray-200 rounded-lg">
                <h4 className="text-md font-medium text-gray-900 mb-4">Add Integration</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Integration Type</label>
                    <select
                      value={newIntegration.integration_type}
                      onChange={(e) => setNewIntegration({ ...newIntegration, integration_type: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    >
                      <option value="">Select Type</option>
                      <option value="bank_api">Bank API</option>
                      <option value="gst_portal">GST Portal</option>
                      <option value="tally">Tally</option>
                      <option value="zoho">Zoho</option>
                      <option value="quickbooks">QuickBooks</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Provider Name</label>
                    <input
                      type="text"
                      value={newIntegration.provider_name}
                      onChange={(e) => setNewIntegration({ ...newIntegration, provider_name: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">API Endpoint</label>
                    <input
                      type="url"
                      value={newIntegration.api_endpoint}
                      onChange={(e) => setNewIntegration({ ...newIntegration, api_endpoint: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Sync Frequency</label>
                    <select
                      value={newIntegration.sync_frequency}
                      onChange={(e) => setNewIntegration({ ...newIntegration, sync_frequency: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                    </select>
                  </div>
                </div>
                <div className="mt-4 flex justify-end space-x-3">
                  <button
                    onClick={() => setShowIntegrationForm(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={createIntegration}
                    disabled={saving}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                  >
                    {saving ? 'Adding...' : 'Add Integration'}
                  </button>
                </div>
              </div>
            )}

            {/* Integrations List */}
            <div className="space-y-4">
              {integrations.length === 0 ? (
                <div className="text-center py-8">
                  <Plug className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">No integrations configured</p>
                </div>
              ) : (
                integrations.map((integration) => (
                  <div key={integration.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-md font-medium text-gray-900">{integration.provider_name}</h4>
                        <p className="text-sm text-gray-500">{integration.integration_type}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${integration.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                          }`}>
                          {integration.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <button className="text-red-600 hover:text-red-900">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-gray-500">
                      <p>Last sync: {integration.last_sync_at ? new Date(integration.last_sync_at).toLocaleDateString() : 'Never'}</p>
                      <p>Frequency: {integration.sync_frequency}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Notification Preferences</h3>

            <div className="space-y-6">
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-4">Email Alerts</h4>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.email_alerts.risk_changes}
                      onChange={(e) => setPreferences({
                        ...preferences,
                        email_alerts: {
                          ...preferences.email_alerts,
                          risk_changes: e.target.checked
                        }
                      })}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Risk score changes</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.email_alerts.credit_alerts}
                      onChange={(e) => setPreferences({
                        ...preferences,
                        email_alerts: {
                          ...preferences.email_alerts,
                          credit_alerts: e.target.checked
                        }
                      })}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Credit alerts</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.email_alerts.reports}
                      onChange={(e) => setPreferences({
                        ...preferences,
                        email_alerts: {
                          ...preferences.email_alerts,
                          reports: e.target.checked
                        }
                      })}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Report generation</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.email_alerts.uploads}
                      onChange={(e) => setPreferences({
                        ...preferences,
                        email_alerts: {
                          ...preferences.email_alerts,
                          uploads: e.target.checked
                        }
                      })}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">File uploads</span>
                  </label>
                </div>
              </div>

              <div>
                <h4 className="text-md font-medium text-gray-900 mb-4">Notification Frequency</h4>
                <select
                  value={preferences.notification_frequency}
                  onChange={(e) => setPreferences({ ...preferences, notification_frequency: e.target.value })}
                  className="mt-1 block w-full max-w-xs rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="immediate">Immediate</option>
                  <option value="daily">Daily Digest</option>
                  <option value="weekly">Weekly Summary</option>
                </select>
              </div>

              <div className="mt-6">
                <button
                  onClick={saveUserPreferences}
                  disabled={saving}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? 'Saving...' : 'Save Preferences'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Localization Tab */}
        {activeTab === 'localization' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Language & Localization</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
                <select
                  value={preferences.language}
                  onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="fr">Français</option>
                  <option value="de">Deutsch</option>
                  <option value="it">Italiano</option>
                  <option value="pt">Português</option>
                  <option value="zh">中文</option>
                  <option value="ja">日本語</option>
                  <option value="ko">한국어</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
                <select
                  value={preferences.timezone}
                  onChange={(e) => setPreferences({ ...preferences, timezone: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">Eastern Time</option>
                  <option value="Europe/London">London</option>
                  <option value="Asia/Tokyo">Tokyo</option>
                  <option value="Asia/Kolkata">India</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date Format</label>
                <select
                  value={preferences.date_format}
                  onChange={(e) => setPreferences({ ...preferences, date_format: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Currency Display</label>
                <select
                  value={preferences.currency_display}
                  onChange={(e) => setPreferences({ ...preferences, currency_display: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="symbol">Symbol ($)</option>
                  <option value="code">Code (USD)</option>
                  <option value="both">Both</option>
                </select>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={saveUserPreferences}
                disabled={saving}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
              >
                <Save className="h-4 w-4 mr-2" />
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Delete Company Modal */}
      <DeleteCompanyModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        company={selectedCompany}
      />
    </div>
  );
};

export default Settings;
