/**
 * Developer Dashboard Component - Phase 5
 * Comprehensive API management, monitoring, and developer tools
 */

import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';
import {
  Code, Key, Activity, Settings, Users, Zap, Database, 
  Globe, Webhook, AlertTriangle, CheckCircle, Clock,
  Copy, Eye, EyeOff, Trash2, Edit3, Plus, RefreshCw,
  TrendingUp, TrendingDown, BarChart3, PieChart as PieChartIcon,
  Bell, Shield, Lock, Unlock, Calendar, Download
} from 'lucide-react';

interface APIKey {
  key_id: string;
  name: string;
  permissions: string[];
  rate_limit: number;
  created_at: string;
  last_used?: string;
  usage_count: number;
  is_active: boolean;
}

interface WebhookEndpoint {
  endpoint_id: string;
  url: string;
  events: string[];
  is_active: boolean;
  success_count: number;
  failure_count: number;
  last_triggered?: string;
}

interface Integration {
  integration_id: string;
  system_type: string;
  name: string;
  status: string;
  last_sync?: string;
  created_at: string;
}

interface DeveloperDashboardProps {
  organizationId: string;
  userRole: string;
}

const DeveloperDashboard: React.FC<DeveloperDashboardProps> = ({
  organizationId,
  userRole
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'api-keys' | 'webhooks' | 'integrations' | 'analytics' | 'documentation'>('overview');
  const [apiKeys, setAPIKeys] = useState<APIKey[]>([]);
  const [webhooks, setWebhooks] = useState<WebhookEndpoint[]>([]);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateAPIKey, setShowCreateAPIKey] = useState(false);
  const [showCreateWebhook, setShowCreateWebhook] = useState(false);
  const [selectedAPIKey, setSelectedAPIKey] = useState<APIKey | null>(null);

  // Sample data for demo
  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true);
      
      // Simulate API calls
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Sample API Keys
      setAPIKeys([
        {
          key_id: 'key_prod_123',
          name: 'Production API Key',
          permissions: ['tutoring:read', 'tutoring:write', 'video:read', 'assessment:read'],
          rate_limit: 10000,
          created_at: '2024-01-15T10:30:00Z',
          last_used: '2024-01-25T14:22:00Z',
          usage_count: 45623,
          is_active: true
        },
        {
          key_id: 'key_dev_456',
          name: 'Development Testing',
          permissions: ['tutoring:read', 'video:read'],
          rate_limit: 1000,
          created_at: '2024-01-20T09:15:00Z',
          last_used: '2024-01-25T16:45:00Z',
          usage_count: 1247,
          is_active: true
        }
      ]);

      // Sample Webhooks
      setWebhooks([
        {
          endpoint_id: 'webhook_001',
          url: 'https://api.myapp.com/webhooks/snaplearn',
          events: ['assessment.completed', 'video.generated'],
          is_active: true,
          success_count: 1234,
          failure_count: 12,
          last_triggered: '2024-01-25T16:30:00Z'
        }
      ]);

      // Sample Integrations
      setIntegrations([
        {
          integration_id: 'int_classroom_001',
          system_type: 'google_classroom',
          name: 'Main Classroom Integration',
          status: 'active',
          last_sync: '2024-01-25T15:00:00Z',
          created_at: '2024-01-10T12:00:00Z'
        },
        {
          integration_id: 'int_slack_001',
          system_type: 'slack',
          name: 'Team Notifications',
          status: 'active',
          last_sync: '2024-01-25T16:45:00Z',
          created_at: '2024-01-12T10:30:00Z'
        }
      ]);

      // Sample Analytics
      setAnalytics({
        api_usage: {
          total_calls: 46870,
          calls_today: 2341,
          success_rate: 99.7,
          average_response_time: 245,
          top_endpoints: [
            { endpoint: '/api/explain', calls: 18234, percentage: 38.9 },
            { endpoint: '/api/video/generate-contextual', calls: 12456, percentage: 26.6 },
            { endpoint: '/api/assessment/create', calls: 8234, percentage: 17.6 },
            { endpoint: '/api/conversation/start', calls: 7946, percentage: 17.0 }
          ]
        },
        error_rates: [
          { time: '00:00', errors: 2, total: 890 },
          { time: '04:00', errors: 1, total: 234 },
          { time: '08:00', errors: 5, total: 1234 },
          { time: '12:00', errors: 3, total: 1567 },
          { time: '16:00', errors: 8, total: 1890 },
          { time: '20:00', errors: 4, total: 1123 }
        ],
        webhook_stats: {
          total_delivered: 1234,
          success_rate: 99.0,
          average_response_time: 189
        }
      });

      setIsLoading(false);
    };

    loadDashboardData();
  }, [organizationId]);

  const handleCreateAPIKey = async (keyData: any) => {
    // Simulate API call
    const newKey: APIKey = {
      key_id: `key_${Date.now()}`,
      name: keyData.name,
      permissions: keyData.permissions,
      rate_limit: keyData.rateLimit,
      created_at: new Date().toISOString(),
      usage_count: 0,
      is_active: true
    };
    
    setAPIKeys(prev => [...prev, newKey]);
    setShowCreateAPIKey(false);
  };

  const handleCreateWebhook = async (webhookData: any) => {
    // Simulate API call
    const newWebhook: WebhookEndpoint = {
      endpoint_id: `webhook_${Date.now()}`,
      url: webhookData.url,
      events: webhookData.events,
      is_active: true,
      success_count: 0,
      failure_count: 0
    };
    
    setWebhooks(prev => [...prev, newWebhook]);
    setShowCreateWebhook(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Developer Dashboard</h1>
            <p className="text-blue-100">Manage APIs, monitor usage, and configure integrations</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm text-blue-200">Organization</div>
              <div className="font-semibold">{organizationId}</div>
            </div>
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Code className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'api-keys', label: 'API Keys', icon: Key },
            { id: 'webhooks', label: 'Webhooks', icon: Webhook },
            { id: 'integrations', label: 'Integrations', icon: Globe },
            { id: 'analytics', label: 'Analytics', icon: Activity },
            { id: 'documentation', label: 'Docs', icon: Code }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">API Calls Today</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics?.api_usage.calls_today.toLocaleString()}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Activity className="w-6 h-6 text-blue-600" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-green-500">+12%</span>
                <span className="text-gray-500 ml-1">from yesterday</span>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics?.api_usage.success_rate}%</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-green-500">+0.2%</span>
                <span className="text-gray-500 ml-1">this week</span>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active API Keys</p>
                  <p className="text-2xl font-bold text-gray-900">{apiKeys.filter(k => k.is_active).length}</p>
                </div>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Key className="w-6 h-6 text-purple-600" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <span className="text-gray-500">Total: {apiKeys.length}</span>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics?.api_usage.average_response_time}ms</p>
                </div>
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <Clock className="w-6 h-6 text-orange-600" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-sm">
                <TrendingDown className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-green-500">-15ms</span>
                <span className="text-gray-500 ml-1">improved</span>
              </div>
            </div>
          </div>

          {/* API Usage Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">Top API Endpoints</h3>
              <div className="space-y-4">
                {analytics?.api_usage.top_endpoints.map((endpoint: any, index: number) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-900">{endpoint.endpoint}</span>
                        <span className="text-sm text-gray-500">{endpoint.calls.toLocaleString()}</span>
                      </div>
                      <div className="mt-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 rounded-full h-2" 
                          style={{ width: `${endpoint.percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">Error Rate Trends</h3>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={analytics?.error_rates}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="errors" stackId="1" stroke="#ef4444" fill="#fee2e2" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg p-6 border border-gray-200">
            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
            <div className="space-y-4">
              {[
                { type: 'api_key', message: 'New API key "Mobile App Key" created', time: '2 hours ago', icon: Key },
                { type: 'webhook', message: 'Webhook endpoint received 45 events successfully', time: '4 hours ago', icon: Webhook },
                { type: 'integration', message: 'Google Classroom sync completed', time: '6 hours ago', icon: Globe },
                { type: 'error', message: 'Rate limit exceeded for API key prod_123', time: '1 day ago', icon: AlertTriangle }
              ].map((activity, index) => {
                const Icon = activity.icon;
                return (
                  <div key={index} className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      activity.type === 'error' ? 'bg-red-100' : 'bg-blue-100'
                    }`}>
                      <Icon className={`w-5 h-5 ${
                        activity.type === 'error' ? 'text-red-600' : 'text-blue-600'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                      <p className="text-xs text-gray-500">{activity.time}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* API Keys Tab */}
      {activeTab === 'api-keys' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">API Keys</h2>
            <button
              onClick={() => setShowCreateAPIKey(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Create API Key</span>
            </button>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Permissions</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usage</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Used</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {apiKeys.map((key) => (
                    <tr key={key.key_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{key.name}</div>
                          <div className="text-sm text-gray-500">•••••••••{key.key_id.slice(-8)}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {key.permissions.map(permission => (
                            <span key={permission} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                              {permission}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{key.usage_count.toLocaleString()} calls</div>
                        <div className="text-sm text-gray-500">Limit: {key.rate_limit}/hour</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                          key.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {key.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => setSelectedAPIKey(key)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button className="text-gray-600 hover:text-gray-900">
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button className="text-red-600 hover:text-red-900">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Webhooks Tab */}
      {activeTab === 'webhooks' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">Webhook Endpoints</h2>
            <button
              onClick={() => setShowCreateWebhook(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Add Webhook</span>
            </button>
          </div>

          <div className="grid gap-6">
            {webhooks.map((webhook) => (
              <div key={webhook.endpoint_id} className="bg-white rounded-lg p-6 border border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className={`w-3 h-3 rounded-full ${
                        webhook.is_active ? 'bg-green-500' : 'bg-red-500'
                      }`} />
                      <h3 className="text-lg font-semibold text-gray-900">Webhook Endpoint</h3>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                        webhook.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {webhook.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3 font-mono bg-gray-50 p-2 rounded">
                      {webhook.url}
                    </p>
                    
                    <div className="mb-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Events:</p>
                      <div className="flex flex-wrap gap-2">
                        {webhook.events.map(event => (
                          <span key={event} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800">
                            {event}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Successful Deliveries</p>
                        <p className="font-semibold text-green-600">{webhook.success_count.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Failed Deliveries</p>
                        <p className="font-semibold text-red-600">{webhook.failure_count.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Last Triggered</p>
                        <p className="font-semibold">
                          {webhook.last_triggered ? new Date(webhook.last_triggered).toLocaleString() : 'Never'}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded">
                      <Zap className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded">
                      <Settings className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-red-600 hover:text-red-900 hover:bg-red-50 rounded">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Integrations Tab */}
      {activeTab === 'integrations' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">External Integrations</h2>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Add Integration</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {integrations.map((integration) => (
              <div key={integration.integration_id} className="bg-white rounded-lg p-6 border border-gray-200">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Globe className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{integration.name}</h3>
                      <p className="text-sm text-gray-500 capitalize">{integration.system_type.replace('_', ' ')}</p>
                    </div>
                  </div>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                    integration.status === 'active' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {integration.status}
                  </span>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Last Sync:</span>
                    <span className="text-gray-900">
                      {integration.last_sync ? new Date(integration.last_sync).toLocaleDateString() : 'Never'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Created:</span>
                    <span className="text-gray-900">{new Date(integration.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="mt-4 flex items-center space-x-2">
                  <button className="flex-1 bg-blue-50 text-blue-600 py-2 px-3 rounded text-sm hover:bg-blue-100">
                    Configure
                  </button>
                  <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded">
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}

            {/* Add Integration Card */}
            <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-6 flex items-center justify-center hover:border-gray-400 cursor-pointer">
              <div className="text-center">
                <Plus className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-sm font-medium text-gray-900 mb-2">Add Integration</h3>
                <p className="text-xs text-gray-500">Connect with external services</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900">API Analytics</h2>
          
          {/* Detailed Analytics Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">API Calls Over Time</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics?.error_rates}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="total" stroke="#3b82f6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">Endpoint Usage Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analytics?.api_usage.top_endpoints}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="calls"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {analytics?.api_usage.top_endpoints.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={['#3b82f6', '#10b981', '#f59e0b', '#ef4444'][index % 4]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="bg-white rounded-lg p-6 border border-gray-200">
            <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">{analytics?.api_usage.total_calls.toLocaleString()}</p>
                <p className="text-sm text-gray-500">Total API Calls</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">{analytics?.api_usage.success_rate}%</p>
                <p className="text-sm text-gray-500">Success Rate</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-orange-600">{analytics?.api_usage.average_response_time}ms</p>
                <p className="text-sm text-gray-500">Avg Response Time</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-purple-600">{analytics?.webhook_stats.total_delivered}</p>
                <p className="text-sm text-gray-500">Webhooks Delivered</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Documentation Tab */}
      {activeTab === 'documentation' && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900">API Documentation</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Quick Start Guide */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white rounded-lg p-6 border border-gray-200">
                <h3 className="text-xl font-semibold mb-4">Quick Start Guide</h3>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">1. Get your API key</h4>
                    <p className="text-sm text-gray-600 mb-2">Create an API key from the API Keys tab above.</p>
                    <div className="bg-gray-50 p-3 rounded font-mono text-sm">
                      curl -H "Authorization: Bearer YOUR_API_KEY" \<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;"https://api.snaplearn.ai/health"
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">2. Make your first request</h4>
                    <p className="text-sm text-gray-600 mb-2">Try generating an AI explanation:</p>
                    <div className="bg-gray-50 p-3 rounded font-mono text-sm">
                      curl -X POST "https://api.snaplearn.ai/api/explain" \<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;-H "Authorization: Bearer YOUR_API_KEY" \<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;-H "Content-Type: application/json" \<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;-d '{{'}<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"question": "What is photosynthesis?",<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"student_id": "demo_student",<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"grade_level": "8"<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;{'}'}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">3. Handle responses</h4>
                    <p className="text-sm text-gray-600 mb-2">All API responses follow a consistent format:</p>
                    <div className="bg-gray-50 p-3 rounded font-mono text-sm">
                      {JSON.stringify({
                        explanation_text: "Photosynthesis is the process...",
                        key_concepts: ["chloroplast", "sunlight", "glucose"],
                        difficulty_level: "appropriate",
                        follow_up_questions: ["How do plants use glucose?"]
                      }, null, 2)}
                    </div>
                  </div>
                </div>
              </div>

              {/* SDK Examples */}
              <div className="bg-white rounded-lg p-6 border border-gray-200">
                <h3 className="text-xl font-semibold mb-4">SDK Examples</h3>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">JavaScript SDK</h4>
                    <div className="bg-gray-50 p-3 rounded font-mono text-sm">
                      import {'{'}SnapLearnAI{'}'} from 'snaplearn-ai-sdk';<br/><br/>
                      
                      const snaplearn = new SnapLearnAI({'{'}apiKey: 'your-key'{'}'});<br/><br/>
                      
                      const explanation = await snaplearn.tutoring.generateExplanation(<br/>
                      &nbsp;&nbsp;'What is gravity?',<br/>
                      &nbsp;&nbsp;{'{'} studentId: 'student_123', gradeLevel: '5' {'}'}<br/>
                      );
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Python SDK</h4>
                    <div className="bg-gray-50 p-3 rounded font-mono text-sm">
                      from snaplearn_ai_sdk import SnapLearnAI<br/><br/>
                      
                      snaplearn = SnapLearnAI(api_key='your-key')<br/><br/>
                      
                      explanation = await snaplearn.tutoring.generate_explanation(<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;question='What is gravity?',<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;student_id='student_123',<br/>
                      &nbsp;&nbsp;&nbsp;&nbsp;grade_level='5'<br/>
                      )
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* API Reference Links */}
            <div className="space-y-6">
              <div className="bg-white rounded-lg p-6 border border-gray-200">
                <h3 className="text-lg font-semibold mb-4">API Reference</h3>
                <div className="space-y-3">
                  {[
                    { name: 'Core Tutoring', endpoint: '/api/explain' },
                    { name: 'Multimodal Input', endpoint: '/api/process-*' },
                    { name: 'Conversations', endpoint: '/api/conversation/*' },
                    { name: 'Assessments', endpoint: '/api/assessment/*' },
                    { name: 'Video Generation', endpoint: '/api/video/*' },
                    { name: 'Analytics', endpoint: '/api/analytics/*' }
                  ].map((item, index) => (
                    <a
                      key={index}
                      href={`/docs#${item.endpoint}`}
                      className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg border border-gray-100"
                    >
                      <span className="text-sm font-medium">{item.name}</span>
                      <span className="text-xs text-gray-500 font-mono">{item.endpoint}</span>
                    </a>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-lg p-6 border border-gray-200">
                <h3 className="text-lg font-semibold mb-4">Resources</h3>
                <div className="space-y-3">
                  <a href="/docs" className="flex items-center space-x-2 text-blue-600 hover:text-blue-800">
                    <Code className="w-4 h-4" />
                    <span>Full API Documentation</span>
                  </a>
                  <a href="/sdk" className="flex items-center space-x-2 text-blue-600 hover:text-blue-800">
                    <Download className="w-4 h-4" />
                    <span>Download SDKs</span>
                  </a>
                  <a href="/demo" className="flex items-center space-x-2 text-blue-600 hover:text-blue-800">
                    <Activity className="w-4 h-4" />
                    <span>Interactive Demo</span>
                  </a>
                  <a href="/support" className="flex items-center space-x-2 text-blue-600 hover:text-blue-800">
                    <Bell className="w-4 h-4" />
                    <span>Developer Support</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create API Key Modal */}
      {showCreateAPIKey && (
        <CreateAPIKeyModal
          onClose={() => setShowCreateAPIKey(false)}
          onSubmit={handleCreateAPIKey}
        />
      )}

      {/* Create Webhook Modal */}
      {showCreateWebhook && (
        <CreateWebhookModal
          onClose={() => setShowCreateWebhook(false)}
          onSubmit={handleCreateWebhook}
        />
      )}
    </div>
  );
};

// Create API Key Modal Component
const CreateAPIKeyModal: React.FC<{
  onClose: () => void;
  onSubmit: (data: any) => void;
}> = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    permissions: [] as string[],
    rateLimit: 1000,
    expiresAt: ''
  });

  const availablePermissions = [
    'tutoring:read', 'tutoring:write',
    'assessment:read', 'assessment:write',
    'video:read', 'video:write',
    'analytics:read', 'student:read'
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Create New API Key</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg"
              placeholder="My API Key"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Permissions</label>
            <div className="space-y-2">
              {availablePermissions.map(permission => (
                <label key={permission} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.permissions.includes(permission)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormData(prev => ({
                          ...prev,
                          permissions: [...prev.permissions, permission]
                        }));
                      } else {
                        setFormData(prev => ({
                          ...prev,
                          permissions: prev.permissions.filter(p => p !== permission)
                        }));
                      }
                    }}
                    className="rounded"
                  />
                  <span className="text-sm">{permission}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Rate Limit (per hour)</label>
            <input
              type="number"
              value={formData.rateLimit}
              onChange={(e) => setFormData(prev => ({ ...prev, rateLimit: parseInt(e.target.value) }))}
              className="w-full p-2 border border-gray-300 rounded-lg"
              min="100"
              max="100000"
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Key
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Create Webhook Modal Component
const CreateWebhookModal: React.FC<{
  onClose: () => void;
  onSubmit: (data: any) => void;
}> = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    url: '',
    events: [] as string[]
  });

  const availableEvents = [
    'assessment.completed', 'video.generated', 'conversation.started',
    'learning.milestone', 'certification.earned', 'batch.completed'
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Add Webhook Endpoint</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Webhook URL</label>
            <input
              type="url"
              value={formData.url}
              onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg"
              placeholder="https://your-app.com/webhooks/snaplearn"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Events</label>
            <div className="space-y-2">
              {availableEvents.map(event => (
                <label key={event} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.events.includes(event)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormData(prev => ({
                          ...prev,
                          events: [...prev.events, event]
                        }));
                      } else {
                        setFormData(prev => ({
                          ...prev,
                          events: prev.events.filter(ev => ev !== event)
                        }));
                      }
                    }}
                    className="rounded"
                  />
                  <span className="text-sm">{event}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Add Webhook
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DeveloperDashboard;