// ProtectedRoute.jsx
import React from "react";
import { Navigate, useLocation } from 'react-router-dom';

export default function ProtectedRoute({ children, isAuthenticated, isLoading}) {
    const location = useLocation();

    if (isLoading){
        return <div className="loading-screen">Loading Pulsecheck...</div>
    }

    if (!isAuthenticated){
        return <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} replace/>;
    }

    return children;
}