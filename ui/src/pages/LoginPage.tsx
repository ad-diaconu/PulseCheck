import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import LoginForm, {type SigningData} from '../components/LoginForm'
import { useAuth } from '../context/AuthContext'
import {api} from '../services/api'

const LoginPage = () => {
    
    const {login} = useAuth()
    const [error, setError] = useState<string|null>(null);
    const navigate = useNavigate();

    const handleLogin = async( data: SigningData, resetForm: () => void) => {
        setError(null);
        try {
            const response = await api.post('/login', data);
            login()
            navigate('/dashboard');
        } catch (err: any) {
            setError(err.message || 'Invalid email or password');
        }
    };

    return (
        <LoginForm onSubmit={handleLogin} error={error} />
    )
}

export default LoginPage;
