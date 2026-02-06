import React from 'react';
import { Bell } from 'lucide-react';

const Notifications = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
        <p className="text-gray-600 mt-1">Stay updated with your financial insights and alerts</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-8 text-center">
        <Bell className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No notifications yet</h3>
        <p className="text-gray-600">
          You're all caught up! We'll notify you here when there are important updates about your financial data, reports, or account activity.
        </p>
      </div>
    </div>
  );
};

export default Notifications;
