import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { 
  Mail, 
  Send, 
  Star, 
  Archive, 
  Trash2, 
  Settings, 
  Plus,
  Search,
  LogOut
} from 'lucide-react'

const Dashboard = () => {
  const { user, logout } = useAuthStore()
  const [activeFolder, setActiveFolder] = useState('inbox')

  const handleLogout = () => {
    logout()
  }

  const folders = [
    { id: 'inbox', name: 'Inbox', icon: Mail, count: 12 },
    { id: 'sent', name: 'Sent', icon: Send, count: 45 },
    { id: 'starred', name: 'Starred', icon: Star, count: 3 },
    { id: 'archive', name: 'Archive', icon: Archive, count: 128 },
    { id: 'trash', name: 'Trash', icon: Trash2, count: 7 },
  ]

  // Mock email data
  const emails = [
    {
      id: 1,
      sender: 'John Smith',
      subject: 'Welcome to your email client!',
      preview: 'Thanks for setting up your personal email client. Here are some tips to get started...',
      time: '2 min ago',
      isRead: false,
      isStarred: false,
    },
    {
      id: 2,
      sender: 'System Notifications',
      subject: 'Server configuration complete',
      preview: 'Your IMAP, POP3, and SMTP settings have been successfully configured...',
      time: '1 hour ago',
      isRead: true,
      isStarred: true,
    },
    {
      id: 3,
      sender: 'Team Update',
      subject: 'Weekly newsletter',
      preview: 'Check out the latest updates and features in our weekly newsletter...',
      time: 'Yesterday',
      isRead: true,
      isStarred: false,
    },
  ]

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <Mail className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-gray-900">Email Client</h1>
              <p className="text-sm text-gray-500">{user?.username}</p>
            </div>
          </div>
        </div>

        {/* Compose Button */}
        <div className="p-4">
          <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Compose</span>
          </button>
        </div>

        {/* Folders */}
        <div className="flex-1 px-4">
          <nav className="space-y-1">
            {folders.map((folder) => (
              <button
                key={folder.id}
                onClick={() => setActiveFolder(folder.id)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-colors ${
                  activeFolder === folder.id
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <folder.icon className="w-5 h-5" />
                  <span className="font-medium">{folder.name}</span>
                </div>
                {folder.count > 0 && (
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    activeFolder === folder.id
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {folder.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Bottom Actions */}
        <div className="p-4 border-t border-gray-200 space-y-2">
          <button className="w-full flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
            <Settings className="w-5 h-5" />
            <span>Settings</span>
          </button>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 capitalize">
              {activeFolder}
            </h2>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search emails..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-64"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Email List */}
        <div className="flex-1 overflow-y-auto">
          <div className="bg-white">
            {emails.map((email) => (
              <div
                key={email.id}
                className={`p-6 border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors ${
                  !email.isRead ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                      {email.sender.charAt(0)}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className={`text-sm ${!email.isRead ? 'font-semibold text-gray-900' : 'font-medium text-gray-700'}`}>
                        {email.sender}
                      </p>
                      <div className="flex items-center space-x-2">
                        {email.isStarred && (
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                        )}
                        <span className="text-sm text-gray-500">{email.time}</span>
                      </div>
                    </div>
                    <p className={`text-sm mb-1 ${!email.isRead ? 'font-semibold text-gray-900' : 'text-gray-700'}`}>
                      {email.subject}
                    </p>
                    <p className="text-sm text-gray-500 line-clamp-2">
                      {email.preview}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Empty State */}
          {emails.length === 0 && (
            <div className="flex-1 flex items-center justify-center p-8">
              <div className="text-center">
                <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No emails</h3>
                <p className="text-gray-500">
                  {activeFolder === 'inbox' 
                    ? "You don't have any emails in your inbox."
                    : `No emails in ${activeFolder}.`
                  }
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
