import { useState } from 'react'
import { ArrowLeft, Plus, Settings as SettingsIcon, User, Mail } from 'lucide-react'
import { Link } from 'react-router-dom'

const Settings = () => {
  const [activeTab, setActiveTab] = useState('accounts')

  const tabs = [
    { id: 'accounts', name: 'Email Accounts', icon: Mail },
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'general', name: 'General', icon: SettingsIcon },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Link 
                to="/dashboard" 
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex space-x-8">
          {/* Sidebar */}
          <div className="w-64 flex-shrink-0">
            <nav className="bg-white rounded-lg shadow p-4">
              <ul className="space-y-2">
                {tabs.map((tab) => (
                  <li key={tab.id}>
                    <button
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                        activeTab === tab.id
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <tab.icon className="w-5 h-5" />
                      <span className="font-medium">{tab.name}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {activeTab === 'accounts' && <EmailAccountsTab />}
            {activeTab === 'profile' && <ProfileTab />}
            {activeTab === 'general' && <GeneralTab />}
          </div>
        </div>
      </div>
    </div>
  )
}

const EmailAccountsTab = () => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Email Accounts</h2>
            <p className="text-sm text-gray-600">Manage your email accounts and server settings</p>
          </div>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Add Account</span>
          </button>
        </div>
      </div>

      <div className="p-6">
        <div className="text-center py-12">
          <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No email accounts</h3>
          <p className="text-gray-500 mb-4">
            Get started by adding your first email account.
          </p>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
            Add Your First Account
          </button>
        </div>
      </div>
    </div>
  )
}

const ProfileTab = () => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Profile Settings</h2>
        <p className="text-sm text-gray-600">Update your personal information</p>
      </div>

      <div className="p-6">
        <form className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Profile Picture
            </label>
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
                <User className="w-8 h-8 text-gray-400" />
              </div>
              <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                Change Picture
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Your full name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Your username"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="your@email.com"
            />
          </div>

          <div className="pt-4">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const GeneralTab = () => {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">General Settings</h2>
        <p className="text-sm text-gray-600">Customize your email client experience</p>
      </div>

      <div className="p-6">
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-3">Appearance</h3>
            <div className="space-y-3">
              <label className="flex items-center">
                <input type="radio" name="theme" className="mr-3" defaultChecked />
                <span className="text-sm text-gray-700">Light mode</span>
              </label>
              <label className="flex items-center">
                <input type="radio" name="theme" className="mr-3" />
                <span className="text-sm text-gray-700">Dark mode</span>
              </label>
              <label className="flex items-center">
                <input type="radio" name="theme" className="mr-3" />
                <span className="text-sm text-gray-700">System default</span>
              </label>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-3">Notifications</h3>
            <div className="space-y-3">
              <label className="flex items-center">
                <input type="checkbox" className="mr-3" defaultChecked />
                <span className="text-sm text-gray-700">Desktop notifications</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="mr-3" defaultChecked />
                <span className="text-sm text-gray-700">Sound notifications</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="mr-3" />
                <span className="text-sm text-gray-700">Email previews in notifications</span>
              </label>
            </div>
          </div>

          <div className="pt-4">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors">
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
