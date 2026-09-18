import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import LoginForm, {type SigningData} from '../components/LoginForm'
import { useAuth } from '../context/useAuth'
import {api} from '../services/api'
import { ApiError, AppError } from '../utils/errors'

const LoginPage = () => {
    
    const {login} = useAuth()
    const [error, setError] = useState<string|null>(null);
    const navigate = useNavigate();

    // eslint-disable-next-line @typescript-eslint/no-unused-vars -- required by LoginForm's onSubmit signature
    const handleLogin = async( data: SigningData, _resetForm: () => void) => {
        setError(null);
        try {
            await api.post('/login', data);
            login()
            navigate('/dashboard');
        } catch (err: unknown) {
            if (err instanceof ApiError) {
                setError(err.message);
            } else if (err instanceof AppError) {
                setError('Network error. Please verify your connection...');
            } else {
                setError('Invalid email or password');
            }
        }
    };

    return (
        <LoginForm onSubmit={handleLogin} error={error} />
    )
}

export default LoginPage;
