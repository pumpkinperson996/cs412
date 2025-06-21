// src/components/Navbar.jsx
import { Link, useNavigate } from 'react-router-dom';
import { FaHome, FaUser, FaSignOutAlt } from 'react-icons/fa';

export default function Navbar({ currentUser, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Title */}
          <Link to="/" className="text-xl font-bold text-gray-800">
            Restroom Rating System
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-6">
            <Link 
              to="/" 
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              <FaHome className="mr-2" />
              Home
            </Link>

            <Link 
              to="/profile" 
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              <FaUser className="mr-2" />
              {currentUser?.username}
            </Link>

            <button
              onClick={handleLogout}
              className="flex items-center text-red-600 hover:text-red-700"
            >
              <FaSignOutAlt className="mr-2" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}