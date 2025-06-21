// src/components/RestroomCard.jsx
import { FaStar, FaMapMarkerAlt } from 'react-icons/fa';

export default function RestroomCard({ restroom, onClick }) {
  return (
    <div 
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
      onClick={() => onClick(restroom.id)}
    >
      <h3 className="text-lg font-semibold mb-2">{restroom.name}</h3>
      
      <div className="flex items-center text-gray-600 mb-2">
        <FaMapMarkerAlt className="mr-2" />
        <p className="text-sm">{restroom.address}</p>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <FaStar className="text-yellow-500 mr-1" />
          <span>{restroom.avg_rating?.toFixed(1) || 'No rating'}</span>
        </div>
        <span className="text-sm text-gray-500">
          {restroom.stall_count || 0} stalls
        </span>
      </div>
    </div>
  );
}