import { useParams } from 'react-router-dom'
import EmailViewer from '../components/EmailViewer'

const EmailPage = () => {
  const { emailId } = useParams<{ emailId: string }>()
  
  return (
    <EmailViewer 
      emailId={emailId ? parseInt(emailId) : undefined}
      isStandalone={true}
    />
  )
}

export default EmailPage
