import { Link } from 'react-router-dom'

const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h1 className="text-6xl font-bold text-primary-600 mb-4">404</h1>
      <p className="text-xl mb-8">Page not found</p>
      <Link 
        to="/"
        className="px-4 py-2 rounded bg-primary-600 hover:bg-primary-700 text-white"
      >
        Go Home
      </Link>
    </div>
  )
}

export default NotFound