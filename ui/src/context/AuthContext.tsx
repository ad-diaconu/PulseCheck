import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import {api} from '../services/api';

type AuthContextType = {
    isAuthenticated: boolean;
    isLoading: boolean;
    login: () => void;
    logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({children}: {children: React.ReactNode}) => {

    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

    useEffect(()=>{
        const fetchAuth = async() => {
            try{
                await api.get("/me");
                setIsAuthenticated(true)
            }catch(error:any){
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
        }catch(error:any){
            console.log(error)
            throw new Error('Logout process could not be done.')
        }
    }

    return (
        <AuthContext.Provider value={{isAuthenticated, isLoading, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
}               

export const useAuth = () => {
    const context = useContext(AuthContext);
    if(!context) throw new Error('useAuthmust be used within AuthProvider');
    return context;
}