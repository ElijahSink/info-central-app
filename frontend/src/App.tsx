import { useState } from 'react'
import { Dashboard } from './components/Dashboard'
import { Toaster } from './components/ui/toaster'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Info Central</h1>
          <p className="text-muted-foreground">AI-powered dashboard builder</p>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-6">
        <Dashboard />
      </main>
      
      <Toaster />
    </div>
  )
}

export default App