import axios from 'axios';
import { ApiError, AppError } from '../utils/errors';
import { logger } from "../utils/logger"

export const api = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: true,
})

api.interceptors.response.use(
    (response) => response,
    (error) => {
        // network error
        if (!error.response) {
            logger.error('Network Error', error)
            throw new AppError("Can not connect to server")
        }

        const status = error.response.status;
        const detail = error.response.data?.detail || 'Unknown Server Error'
        logger.warning(`API Error ${status}: ${detail}`)

        // A 401 on /login or /register means "wrong credentials" — that's
        // handled locally by the form already, it's not an expired session.
        const requestUrl: string = error.config?.url ?? '';
        const isAuthEndpoint = requestUrl.includes('/login') || requestUrl.includes('/register');

        // Avoid redirecting if we're already on /login — otherwise a 401
        // from a request made ON the login page (e.g. wrong password,
        // though that's excluded above too) could trigger a redirect loop.
        const isAlreadyOnLoginPage = window.location.pathname === '/login';

        if (status === 401 && !isAuthEndpoint && !isAlreadyOnLoginPage) {
            // Session expired while the app was open (e.g. cookie expired
            // mid-use, as opposed to never having been logged in). Every
            // piece of React state that assumed "authenticated" is now
            // stale/wrong, so a full reload — not a React navigate() — is
            // the clean way to reset everything back to a known state.
            window.location.href = '/login'
        }

        // formatted error that can be used by any component
        throw new ApiError(detail, status, error.response.data)

    }
)