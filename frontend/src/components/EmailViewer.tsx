import { useState } from 'react'
import { X, Star, Reply, Forward, Trash2, Archive, ChevronLeft, ChevronRight, Mail } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { useEmail, useUpdateEmail } from '../hooks/useEmails'
import { Email } from '../services/api'

interface EmailViewerProps {
  emailId: number
  onClose: () => void
  onNext?: () => void
  onPrevious?: () => void
  hasNext?: boolean
  hasPrevious?: boolean
}

const EmailViewer = ({ 
  emailId, 
  onClose, 
  onNext, 
  onPrevious, 
  hasNext = false, 
  hasPrevious = false 
}: EmailViewerProps) => {
  const { data: email, isLoading, error } = useEmail(emailId)
  const updateEmailMutation = useUpdateEmail()
  const [showRawHeaders, setShowRawHeaders] = useState(false)

  const handleStarToggle = () => {
    if (email) {
      updateEmailMutation.mutate({
        emailId: email.id,
        updates: { is_starred: !email.is_starred }
      })
    }
  }

  const handleMarkUnread = () => {
    if (email) {
      updateEmailMutation.mutate({
        emailId: email.id,
        updates: { is_read: false }
      })
    }
  }

  const handleDelete = () => {
    if (email && confirm('Are you sure you want to delete this email?')) {
      updateEmailMutation.mutate({
        emailId: email.id,
        updates: { is_deleted: true }
      }, {
        onSuccess: () => onClose()
      })
    }
  }

  const handleArchive = () => {
    if (email) {
      updateEmailMutation.mutate({
        emailId: email.id,
        updates: { folder: 'ARCHIVE' }
      }, {
        onSuccess: () => onClose()
      })
    }
  }

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading email...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error || !email) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
          <div className="text-center">
            <h3 className="text-lg font-medium text-red-600 mb-2">Error Loading Email</h3>
            <p className="text-gray-600 mb-4">
              {error?.message || 'Failed to load email content'}
            </p>
            <button 
              onClick={onClose}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={onPrevious}
                disabled={!hasPrevious}
                className="p-2 hover:bg-gray-100 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                title="Previous email"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={onNext}
                disabled={!hasNext}
                className="p-2 hover:bg-gray-100 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                title="Next email"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
            <div className="h-6 border-l border-gray-300" />
            <h2 className="text-lg font-semibold text-gray-900 truncate">
              {email.subject || '(No Subject)'}
            </h2>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleStarToggle}
              className="flex items-center space-x-1 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 rounded-lg border border-gray-300 transition-colors"
              title={email.is_starred ? 'Remove star' : 'Add star'}
            >
              <Star className={`w-4 h-4 ${email.is_starred ? 'text-yellow-500 fill-current' : 'text-gray-400'}`} />
              <span>{email.is_starred ? 'Starred' : 'Star'}</span>
            </button>
            <button
              onClick={() => {/* TODO: Implement reply */}}
              className="flex items-center space-x-1 px-3 py-1.5 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 rounded-lg border border-gray-300 transition-colors"
              title="Reply"
            >
              <Reply className="w-4 h-4" />
              <span>Reply</span>
            </button>
            <button
              onClick={() => {/* TODO: Implement forward */}}
              className="flex items-center space-x-1 px-3 py-1.5 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 rounded-lg border border-gray-300 transition-colors"
              title="Forward"
            >
              <Forward className="w-4 h-4" />
              <span>Forward</span>
            </button>
            <button
              onClick={handleArchive}
              className="flex items-center space-x-1 px-3 py-1.5 text-sm text-gray-700 hover:bg-green-50 hover:text-green-700 rounded-lg border border-gray-300 transition-colors"
              title="Archive"
            >
              <Archive className="w-4 h-4" />
              <span>Archive</span>
            </button>
            <button
              onClick={handleDelete}
              className="flex items-center space-x-1 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 hover:text-red-700 rounded-lg border border-red-200 transition-colors"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
              <span>Delete</span>
            </button>
            <div className="h-6 border-l border-gray-300 mx-2" />
            <button
              onClick={onClose}
              className="flex items-center space-x-1 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 rounded-lg border border-gray-300 transition-colors"
              title="Close"
            >
              <X className="w-4 h-4" />
              <span>Close</span>
            </button>
          </div>
        </div>

        {/* Email Content */}
        <div className="flex-1 overflow-y-auto">
          {/* Email Header Info */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                {(email.sender_name || email.sender_email).charAt(0).toUpperCase()}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {email.sender_name || email.sender_email}
                    </h3>
                    <p className="text-sm text-gray-600">{email.sender_email}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">
                      {email.date_received 
                        ? formatDistanceToNow(new Date(email.date_received), { addSuffix: true })
                        : 'Unknown date'
                      }
                    </p>
                    {!email.is_read && (
                      <button
                        onClick={handleMarkUnread}
                        className="text-xs text-blue-600 hover:text-blue-700"
                      >
                        Mark as unread
                      </button>
                    )}
                  </div>
                </div>
                
                {/* Recipients */}
                {email.to_addresses && email.to_addresses.length > 0 && (
                  <div className="text-sm text-gray-600 mb-1">
                    <span className="font-medium">To:</span>{' '}
                    {email.to_addresses.map((addr, index) => (
                      <span key={index}>
                        {addr.name ? `${addr.name} <${addr.email}>` : addr.email}
                        {index < email.to_addresses!.length - 1 && ', '}
                      </span>
                    ))}
                  </div>
                )}
                
                {email.cc_addresses && email.cc_addresses.length > 0 && (
                  <div className="text-sm text-gray-600 mb-1">
                    <span className="font-medium">CC:</span>{' '}
                    {email.cc_addresses.map((addr, index) => (
                      <span key={index}>
                        {addr.name ? `${addr.name} <${addr.email}>` : addr.email}
                        {index < email.cc_addresses!.length - 1 && ', '}
                      </span>
                    ))}
                  </div>
                )}

                {/* Attachments */}
                {email.attachments && email.attachments.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-2">
                      Attachments ({email.attachments.length})
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {email.attachments.map((attachment, index) => (
                        <div
                          key={index}
                          className="bg-gray-100 px-3 py-1 rounded-lg text-sm text-gray-700"
                        >
                          {attachment.filename || `Attachment ${index + 1}`}
                          {attachment.size && (
                            <span className="text-gray-500 ml-1">
                              ({Math.round(attachment.size / 1024)}KB)
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Email Body */}
          <div className="p-6">
            {email.body_html ? (
              <div className="prose max-w-none">
                <div 
                  className="border border-gray-200 rounded-lg p-4 bg-white"
                  dangerouslySetInnerHTML={{ __html: email.body_html }}
                  style={{ 
                    maxWidth: '100%',
                    wordWrap: 'break-word',
                    overflowWrap: 'break-word'
                  }}
                />
              </div>
            ) : email.body_text ? (
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <pre className="whitespace-pre-wrap font-sans text-sm text-gray-900 overflow-x-auto">
                  {email.body_text}
                </pre>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium mb-2">No email content available</p>
                <p className="text-sm">This email may not have been fully synced yet.</p>
                <button 
                  onClick={() => window.location.reload()} 
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Refresh
                </button>
              </div>
            )}
          </div>

          {/* Debug Info */}
          <div className="p-6 border-t border-gray-200 bg-gray-50">
            <button
              onClick={() => setShowRawHeaders(!showRawHeaders)}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              {showRawHeaders ? 'Hide' : 'Show'} Email Details
            </button>
            
            {showRawHeaders && (
              <div className="mt-4 bg-white p-4 rounded-lg border text-xs font-mono">
                <div className="space-y-2">
                  <div><strong>Message ID:</strong> {email.message_id}</div>
                  <div><strong>UID:</strong> {email.uid}</div>
                  <div><strong>Date Sent:</strong> {email.date_sent}</div>
                  <div><strong>Date Received:</strong> {email.date_received}</div>
                  <div><strong>Size:</strong> {email.size} bytes</div>
                  <div><strong>Folder:</strong> {email.folder}</div>
                  <div><strong>Read:</strong> {email.is_read ? 'Yes' : 'No'}</div>
                  <div><strong>Starred:</strong> {email.is_starred ? 'Yes' : 'No'}</div>
                  {email.reply_to && <div><strong>Reply-To:</strong> {email.reply_to}</div>}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmailViewer
