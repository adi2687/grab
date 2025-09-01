import React from "react";
import "./App.css";

function Navbar() {
  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <span className="text-xl font-bold text-blue-600">MyApp</span>
          </div>
          <div className="hidden sm:ml-6 sm:flex sm:items-center space-x-4">
            <a href="#" className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600">Home</a>
            <a href="#" className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600">Features</a>
            <a href="#" className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600">About</a>
            <button className="ml-4 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Get Started
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

function Hero() {
  return (
    <div className="bg-white">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
          <span className="block">Welcome to</span>
          <span className="block text-blue-600">My Awesome App</span>
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          Build something amazing with our powerful platform. Get started today and transform your ideas into reality.
        </p>
        <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
          <div className="rounded-md shadow">
            <a href="#" className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10">
              Get started
            </a>
          </div>
          <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
            <a href="#" className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10">
              Learn more
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>
        <Hero />
      </main>
      <footer className="bg-white mt-12">
        <div className="max-w-7xl mx-auto py-12 px-4 overflow-hidden sm:px-6 lg:px-8">
          <p className="mt-8 text-center text-base text-gray-400">
            &copy; 2025 MyApp. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

      {/* Features */}
      <section className="features" id="features">
        <div className="feature">
          <h3>🔒 Secure</h3>
          <p>Your data is safe with enterprise-grade encryption.</p>
        </div>
        <div className="feature">
          <h3>⚡ Fast</h3>
          <p>Instant credit score updates and real-time insights.</p>
        </div>
        <div className="feature">
          <h3>📊 Smart</h3>
          <p>AI-driven suggestions to improve your financial health.</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>© 2025 Grab. All rights reserved.</p>
      </footer>
    </>
  );
}
