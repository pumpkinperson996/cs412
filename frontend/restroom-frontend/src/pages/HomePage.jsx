// src/pages/HomePage.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { restroomAPI } from '../services/api';
import RestroomCard from '../components/RestroomCard';
// import LoadingSpinner from '../components/LoadingSpinner';

export default function HomePage() {
  const [restrooms, setRestrooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchRestrooms();
  }, []);

  const fetchRestrooms = async () => {
    try {
      const response = await restroomAPI.getList();
      setRestrooms(response.data);
    } catch (err) {
      setError('Failed to load restroom list');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRestroomClick = (id) => {
    navigate(`/restroom/${id}`);
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Nearby Restrooms</h1>
        <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">
          Add Restroom
        </button>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      {restrooms.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No restroom data available</p>
          <p className="text-gray-400 mt-2">Be the first to add a restroom!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {restrooms.map(restroom => (
            <RestroomCard
              key={restroom.id}
              restroom={restroom}
              onClick={handleRestroomClick}
            />
          ))}
        </div>
      )}
    </div>
  );
}