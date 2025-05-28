import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useEmailStore } from '../stores/emailStore'
import { useEmailAccounts } from '../hooks/useAccount'
import { useEmails, useUpdateEmail, useSyncEmails } from '../hooks/useEmails'
import EmailViewer from '../components/EmailViewer'
import { 
  Mail, 
  Send, 
  Star, 
  Archive, 
  Trash2, 
  Settings, 
  Plus,
  Search,
  LogOut,
  RefreshCw,
  Loader2,
  AlertCircle
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

const Dashboard = () => {
  const { user, logout } = useAuthStore()
  const { 
    activeFolder, 
    selectedAccountId, 
    searchQuery,
    setActiveFolder, 
    setSelectedAccountId, 
    setSearchQuery,
    setIsComposing 
  } = useEmailStore()

  const [selectedEmailId, setSelectedEmailId] = useState<number | null>(null)

  // Fetch email accounts
  const { data: emailAccounts, isLoading: accountsLoading, error: accountsError } = useEmailAccounts()

  // Set default account if none selected
  useEffect(() => {
    if (emailAccounts && emailAccounts.length > 0 && !selectedAccountId) {
      const defaultAccount = emailAccounts.find(acc => acc.is_default) || emailAccounts[0]
      setSelectedAccountId(defaultAccount.id)
    }
  }, [emailAccounts, selectedAccountId, setSelectedAccountId])

  // Fetch emails for selected account
  const { 
    data: emails, 
    isLoading: emailsLoading, 
    error: emailsError,
    refetch: refetchEmails 
  } = useEmails({
    account_id: selectedAccountId || undefined,
    folder: activeFolder,
    limit: 50
  })

  const updateEmailMutation = useUpdateEmail()
  const syncEmailsMutation = useSyncEmails()

  const handleLogout = () => {
    logout()
  }

  const handleSyncEmails = () => {
    if (selectedAccountId) {
      syncEmailsMutation.mutate({ 
        accountId: selectedAccountId, 
        folder: activeFolder 
      })
    }
  }

  const handleEmailClick = (emailId: number, isRead: boolean) => {
    if (!isRead) {
      updateEmailMutation.mutate({
        emailId,
        updates: { is_read: true }
      })
    }
    setSelectedEmailId(emailId)
  }

  const handleStarToggle = (emailId: number, isStarred: boolean) => {
    updateEmailMutation.mutate({
      emailId,
      updates: { is_starred: !isStarred }
    })
  }

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
    // TODO: Implement actual search functionality
  }

  const handleNextEmail = () => {
    if (!selectedEmailId || !filteredEmails.length) return
    
    const currentIndex = filteredEmails.findIndex(email => email.id === selectedEmailId)
    if (currentIndex < filteredEmails.length - 1) {
      setSelectedEmailId(filteredEmails[currentIndex + 1].id)
    }
  }

  const handlePreviousEmail = () => {
    if (!selectedEmailId || !filteredEmails.length) return
    
    const currentIndex = filteredEmails.findIndex(email => email.id === selectedEmailId)
    if (currentIndex > 0) {
      setSelectedEmailId(filteredEmails[currentIndex - 1].id)
    }
  }

  // Calculate folder counts (simplified - would need real counts from backend)
  const folderCounts = {
    INBOX: emails?.filter(e => e.folder === 'INBOX' && !e.is_deleted).length || 0,
    SENT: emails?.filter(e => e.folder === 'SENT' && !e.is_deleted).length || 0,
    STARRED: emails?.filter(e => e.is_starred && !e.is_deleted).length || 0,
    ARCHIVE: emails?.filter(e => e.folder === 'ARCHIVE' && !e.is_deleted).length || 0,
    TRASH: emails?.filter(e => e.is_deleted).length || 0,
  }

  const folders = [
    { id: 'INBOX', name: 'Inbox', icon: Mail, count: folderCounts.INBOX },
    { id: 'SENT', name: 'Sent', icon: Send, count: folderCounts.SENT },
    { id: 'STARRED', name: 'Starred', icon: Star, count: folderCounts.STARRED },
    { id: 'ARCHIVE', name: 'Archive', icon: Archive, count: folderCounts.ARCHIVE },
    { id: 'TRASH', name: 'Trash', icon: Trash2, count: folderCounts.TRASH },
  ]

  // Show loading state
  if (accountsLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading your email accounts...</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (accountsError) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Accounts</h2>
          <p className="text-gray-600 mb-4">There was an error loading your email accounts.</p>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // Show no accounts state
  if (!emailAccounts || emailAccounts.length === 0) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <Mail className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">No Email Accounts</h2>
          <p className="text-gray-600 mb-6">
            Get started by adding your first email account to begin managing your emails.
          </p>
          <Link 
            to="/settings" 
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Add Email Account
          </Link>
        </div>
      </div>
    )
  }

  const selectedAccount = emailAccounts.find(acc => acc.id === selectedAccountId)
  const filteredEmails = emails?.filter(email => {
    if (activeFolder === 'STARRED') return email.is_starred && !email.is_deleted
    if (activeFolder === 'TRASH') return email.is_deleted
    return email.folder === activeFolder && !email.is_deleted
  }) || []

  const currentEmailIndex = selectedEmailId ? filteredEmails.findIndex(email => email.id === selectedEmailId) : -1

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Email Viewer Modal */}
      {selectedEmailId && (
        <EmailViewer
          emailId={selectedEmailId}
          onClose={() => setSelectedEmailId(null)}
          onNext={handleNextEmail}
          onPrevious={handlePreviousEmail}
          hasNext={currentEmailIndex < filteredEmails.length - 1}
          hasPrevious={currentEmailIndex > 0}
        />
      )}

      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <Mail className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="font-semibold text-gray-900 truncate">Email Client</h1>
              <p className="text-sm text-gray-500 truncate">{user?.username}</p>
            </div>
          </div>
        </div>

        {/* Account Selector */}
        {emailAccounts.length > 1 && (
          <div className="p-4 border-b border-gray-200">
            <select
              value={selectedAccountId || ''}
              onChange={(e) => setSelectedAccountId(Number(e.target.value))}
              className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {emailAccounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name} ({account.email_address})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Compose Button */}
        <div className="p-4">
          <button 
            onClick={() => setIsComposing(true)}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
          >
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
          <Link 
            to="/settings"
            className="w-full flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <Settings className="w-5 h-5" />
            <span>Settings</span>
          </Link>
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
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-semibold text-gray-900 capitalize">
                {activeFolder.toLowerCase()}
              </h2>
              {selectedAccount && (
                <span className="text-sm text-gray-500">
                  {selectedAccount.email_address}
                </span>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleSyncEmails}
                disabled={syncEmailsMutation.isPending}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
                title="Sync emails"
              >
                <RefreshCw className={`w-5 h-5 ${syncEmailsMutation.isPending ? 'animate-spin' : ''}`} />
              </button>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search emails..."
                  value={searchQuery}
                  onChange={handleSearch}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-64"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Email List */}
        <div className="flex-1 overflow-y-auto">
          {emailsLoading ? (
            <div className="flex-1 flex items-center justify-center p-8">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
                <p className="text-gray-600">Loading emails...</p>
              </div>
            </div>
          ) : emailsError ? (
            <div className="flex-1 flex items-center justify-center p-8">
              <div className="text-center">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Emails</h3>
                <p className="text-gray-500 mb-4">There was an error loading your emails.</p>
                <button 
                  onClick={() => refetchEmails()}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : filteredEmails.length === 0 ? (
            <div className="flex-1 flex items-center justify-center p-8">
              <div className="text-center">
                <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No emails</h3>
                <p className="text-gray-500">
                  {searchQuery 
                    ? "No emails match your search criteria."
                    : activeFolder === 'INBOX' 
                    ? "You don't have any emails in your inbox."
                    : `No emails in ${activeFolder.toLowerCase()}.`
                  }
                </p>
                {activeFolder === 'INBOX' && (
                  <button 
                    onClick={handleSyncEmails}
                    disabled={syncEmailsMutation.isPending}
                    className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {syncEmailsMutation.isPending ? 'Syncing...' : 'Sync Emails'}
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white">
              {filteredEmails.map((email) => (
                <div
                  key={email.id}
                  onClick={() => handleEmailClick(email.id, email.is_read)}
                  className={`p-6 border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors ${
                    !email.is_read ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                        {(email.sender_name || email.sender_email).charAt(0).toUpperCase()}
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <p className={`text-sm ${!email.is_read ? 'font-semibold text-gray-900' : 'font-medium text-gray-700'}`}>
                          {email.sender_name || email.sender_email}
                        </p>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleStarToggle(email.id, email.is_starred)
                            }}
                            className="p-1 hover:bg-gray-200 rounded"
                          >
                            <Star className={`w-4 h-4 ${email.is_starred ? 'text-yellow-400 fill-current' : 'text-gray-400'}`} />
                          </button>
                          <span className="text-sm text-gray-500">
                            {email.date_received 
                              ? formatDistanceToNow(new Date(email.date_received), { addSuffix: true })
                              : 'Unknown'
                            }
                          </span>
                        </div>
                      </div>
                      <p className={`text-sm mb-1 ${!email.is_read ? 'font-semibold text-gray-900' : 'text-gray-700'}`}>
                        {email.subject || '(No Subject)'}
                      </p>
                      <p className="text-sm text-gray-500 line-clamp-2">
                        {email.body_text || email.body_html?.replace(/<[^>]*>/g, '') || 'No preview available'}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
