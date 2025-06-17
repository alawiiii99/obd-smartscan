import React, { useState, useEffect } from 'react';
import UploadCSV from './components/UploadCSV';
import ChatBox from './components/ChatBox';

const navItems = [
  { key: 'chat', label: 'Chat' },
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'upload', label: 'Upload Data' },
];

const App = () => {
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });
  const [active, setActive] = useState('dashboard');
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const renderContent = () => {
    if (active === 'dashboard') {
      return (
        <iframe
          title="Metabase Dashboard"
          src="http://192.168.3.244:3000/public/dashboard/79a0e848-3983-4c16-a7af-1d127a97d723"
          frameBorder="0"
          width={dimensions.width}
          height={dimensions.height - 56}
          style={{ display: 'block', border: 'none' }}
          allowFullScreen
        />
      );
    }
    if (active === 'chat') return <ChatBox />;
    if (active === 'upload') return <UploadCSV />;
    return null;
  };

  return (
    <div style={{ padding: 0, margin: 0 }}>
      {/* Navigation Bar */}
      <nav
        style={{
          width: '100%',
          background: '#18181b',
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 1rem',
          height: 56,
          position: 'fixed',
          top: 0,
          left: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <img src="/logo.png" alt="Logo" style={{ height: 45 }} />
          <span style={{ fontWeight: 700, fontSize: 20 }}>OBD SmartScan</span>
        </div>

        <button
          onClick={() => setMenuOpen((v) => !v)}
          className="nav-hamburger"
          style={{
            background: 'none',
            border: 'none',
            color: '#fff',
            fontSize: 28,
            display: 'none',
            cursor: 'pointer',
          }}
        >
          &#9776;
        </button>
        <ul
          className="nav-list"
          style={{
            display: 'flex',
            gap: 24,
            listStyle: 'none',
            margin: 0,
            padding: 0,
          }}
        >
          {navItems.map((item) => (
            <li
              key={item.key}
              style={{
                cursor: 'pointer',
                borderBottom: active === item.key ? '2px solid #fff' : 'none',
                fontWeight: active === item.key ? 600 : 400,
              }}
              onClick={() => setActive(item.key)}
            >
              {item.label}
            </li>
          ))}
        </ul>
      </nav>
      {/* Mobile Menu */}
      <ul
        className="nav-mobile"
        style={{
          display: menuOpen ? 'flex' : 'none',
          flexDirection: 'column',
          position: 'fixed',
          top: 56,
          left: 0,
          width: '100%',
          background: '#18181b',
          color: '#fff',
          listStyle: 'none',
          margin: 0,
          padding: '1rem 0',
          zIndex: 99,
        }}
      >
        {navItems.map((item) => (
          <li
            key={item.key}
            style={{
              cursor: 'pointer',
              padding: '1rem',
              borderBottom: active === item.key ? '2px solid #fff' : 'none',
              fontWeight: active === item.key ? 600 : 400,
            }}
            onClick={() => {
              setActive(item.key);
              setMenuOpen(false);
            }}
          >
            {item.label}
          </li>
        ))}
      </ul>
      {/* Main Content */}
      <div style={{ marginTop: 56 }}>{renderContent()}</div>
      {/* Responsive styles */}
      <style>
        {`
          @media (max-width: 768px) {
            .nav-list {
              display: none !important;
            }
            .nav-hamburger {
              display: block !important;
            }
          }
          @media (min-width: 769px) {
            .nav-mobile {
              display: none !important;
            }
          }
        `}
      </style>
    </div>
  );
};

export default App;
