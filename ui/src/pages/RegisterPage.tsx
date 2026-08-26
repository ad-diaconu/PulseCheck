import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import RegisterForm, { type SignupData } from '../components/RegisterForm'
import { api } from '../services/api'
import { ApiError, AppError } from '../utils/errors';

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const RegisterPage = () => {
    const navigate = useNavigate();
    const [globalError, setGlobalError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);


    const handleSignup = async (data: SignupData, resetForm: () => void) => {
        //reset states at each submit
        setGlobalError(null);
        setSuccessMessage(null);

        try {
            await api.post('/signup', data);
            resetForm();
            for (let i = 3; i > 0; i--) {
                setSuccessMessage(`Registration successful! Redirecting to loading page in ${i}...`)
                await sleep(1000)
            }
            navigate('/auth/login')
        } catch (error: any) {
            if (error instanceof ApiError) {
                if (error.status === 400) {
                    setGlobalError(error.data?.detail || "User already registered.");
                } else if (error.status === 422) {
                    if (error.data && Array.isArray(error.data.detail) && error.data.detail.length > 0) {
                        setGlobalError(error.data.detail[0].msg);
                    } else {
                        setGlobalError("Invalid input data. Please check your fields.");
                    }
                } else if (error.status >= 500) {
                    setGlobalError("Our app is currently down. Please try again later");
                } else {
                    const serverMessage = typeof error.data?.detail === 'string'
                        ? error.data.detail
                        : error.message;
                    setGlobalError(serverMessage);
                }

            } else if (error instanceof AppError) {
                setGlobalError("Network error. Please verify your connection...")
            } else {
                setGlobalError("Unknown error. Please try again later...")
            }

        }
    }

    return (
        <RegisterForm onSubmit={handleSignup} error={globalError} successMessage={successMessage} />
    )
}

export default RegisterPage;
