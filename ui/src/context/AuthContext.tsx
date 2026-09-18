import { useEffect, useState, type ReactNode } from 'react';
import {api} from '../services/api';
import { AuthContext } from './auth-context-definition';

export const AuthProvider = ({children}: {children: ReactNode}) => {

    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

    useEffect(()=>{
        const fetchAuth = async() => {
            try{
                await api.get("/me");
                setIsAuthenticated(true)
            }catch{
                setIsAuthenticated(false);
            }finally{
                setIsLoading(false);
            }
        }
       
        fetchAuth();
    },[]);

    const login = () => {
        setIsAuthenticated(true);
    }

    const logout = async () => {
        try{
            await api.post('/logout')
            setIsAuthenticated(false);
        }catch(error){
            throw new Error('Logout process could not be done.', { cause: error })
        }
    }

    return (
        <AuthContext.Provider value={{isAuthenticated, isLoading, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
}