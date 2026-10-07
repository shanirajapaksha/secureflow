import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/context/AuthContext";
import { authenticate } from "@/lib/api";
export default function AuthPage() {
  const [register, setRegister] = useState(false); const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [username, setUsername] = useState(""); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  const { login } = useAuth(); const navigate = useNavigate();
  const submit = async (event: FormEvent) => { event.preventDefault(); setBusy(true); setError(""); try { const value = await authenticate(register ? "/api/auth/register" : "/api/auth/login", { email, password, ...(register ? { username } : {}) }); login(value.access_token, value.user); navigate("/"); } catch (e) { setError(e instanceof Error ? e.message : "Authentication failed"); } finally { setBusy(false); } };
  return <main className="min-h-screen grid place-items-center bg-background p-4"><form onSubmit={submit} className="w-full max-w-md space-y-4 rounded-lg border bg-card p-7"><h1 className="text-2xl font-bold">SecureFlow AI</h1><p className="text-sm text-muted-foreground">{register ? "Create an account" : "Sign in to the security console"}</p>{register && <Input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} required minLength={3} />}<Input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required /><Input type="password" placeholder="Password (6+ characters)" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} />{error && <p className="text-sm text-destructive">{error}</p>}<Button className="w-full" disabled={busy}>{busy ? "Please wait…" : register ? "Create account" : "Sign in"}</Button><button type="button" className="w-full text-sm text-primary" onClick={() => setRegister(!register)}>{register ? "Already have an account? Sign in" : "Need an account? Register"}</button></form></main>;
}
