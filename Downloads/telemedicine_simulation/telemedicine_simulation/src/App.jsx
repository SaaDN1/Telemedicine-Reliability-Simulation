
import React, { useState, useEffect } from 'react';
import './App.css';


function HumanizationChecklist({ onComplete }) {
  const [clearLanguage, setClearLanguage] = useState(false);
  const [consentRecorded, setConsentRecorded] = useState(false);
  const [accessibilityChecked, setAccessibilityChecked] = useState(false);
  const [manualOverrideAvailable, setManualOverrideAvailable] = useState(false);

  useEffect(() => {
    const all = clearLanguage && consentRecorded && accessibilityChecked && manualOverrideAvailable;
    onComplete && onComplete(all);
  }, [clearLanguage, consentRecorded, accessibilityChecked, manualOverrideAvailable, onComplete]);

  return (
    <div className="checklist">
      <h3 className="checklist-title">Humanization Checklist</h3>

      <label className="checklist-item">
        <input type="checkbox" checked={clearLanguage} onChange={e => setClearLanguage(e.target.checked)} /> Clear language
      </label>

      <label className="checklist-item">
        <input type="checkbox" checked={consentRecorded} onChange={e => setConsentRecorded(e.target.checked)} /> Consent recorded
      </label>

      <label className="checklist-item">
        <input type="checkbox" checked={accessibilityChecked} onChange={e => setAccessibilityChecked(e.target.checked)} /> Accessibility checked
      </label>

      <label className="checklist-item">
        <input type="checkbox" checked={manualOverrideAvailable} onChange={e => setManualOverrideAvailable(e.target.checked)} /> Manual override available
      </label>
    </div>
  );
}

function ChatWindow({ appointmentName, onClose }) {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'doctor', text: `Hi ${appointmentName}, video connection failed. I'm here via chat instead. How can I help you today?` }
  ]);
  const [input, setInput] = useState('');

  function sendMessage() {
    if (!input.trim()) return;
    setMessages(m => [...m, { id: Date.now(), sender: 'patient', text: input }]);
    setInput('');
    // Simulate doctor response
    setTimeout(() => {
      const responses = [
        'I understand. Can you describe your symptoms?',
        'That sounds concerning. When did this start?',
        'I see. Have you tried any treatments?',
        'Let me make a note of that.'
      ];
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      setMessages(m => [...m, { id: Date.now() + 1, sender: 'doctor', text: randomResponse }]);
    }, 600);
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h3 className="chat-title">Chat with Doctor</h3>
        <button className="chat-close" onClick={onClose}>×</button>
      </div>

      <div className="chat-messages">
        {messages.map(msg => (
          <div key={msg.id} className={`chat-message ${msg.sender === 'patient' ? 'chat-message--patient' : 'chat-message--doctor'}`}>
            <div className={`chat-bubble ${msg.sender === 'patient' ? 'chat-bubble--patient' : 'chat-bubble--doctor'}`}>
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      <div className="chat-footer">
        <input
          className="chat-input"
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Type message..."
        />
        <button className="chat-send" onClick={sendMessage} aria-label="Send message">➤</button>
      </div>
    </div>
  );
}

export default function App() {
  const [appointments, setAppointments] = useState([]);
  const [name, setName] = useState('');
  const [time, setTime] = useState('2025-11-25 10:00');
  const [status, setStatus] = useState('idle');
  const [canProceed, setCanProceed] = useState(false);
  const [activeChat, setActiveChat] = useState(null);

  function book() {
    if (!name) return alert('Enter patient name');
    const appt = { id: Date.now(), name, time, status: 'booked' };
    setAppointments(a => [appt, ...a]);
    setName('');
  }

  async function startConsultation(apptId) {
    setStatus('connecting');
    // simulate bad network: 30% chance of failure
    await new Promise(r => setTimeout(r, 1200));
    const fail = Math.random() < 0.30;
    if (fail) {
      setStatus('failed');
      const appt = appointments.find(a => a.id === apptId);
      setActiveChat(apptId);
      // fallback: mark appointment as 'chat-fallback'
      setAppointments(a => a.map(x => x.id === apptId ? { ...x, status: 'chat-fallback' } : x));
    } else {
      setStatus('connected');
      setAppointments(a => a.map(x => x.id === apptId ? { ...x, status: 'in-consultation' } : x));
    }
    setTimeout(() => setStatus('idle'), 1500);
  }

  return (
    <div className="app-container">
      <h1>Telemedicine Reliability Simulation</h1>
      <p className="lead">Simple simulation: book an appointment, then attempt to start consultation. The system randomly fails to connect to demonstrate fallback behavior.</p>

      <div className="main-grid">
        <div className="left-column">
          <h3>Book Appointment</h3>
          <input className="text-input" placeholder="Patient name" value={name} onChange={e => setName(e.target.value)} />
          <input className="text-input" type="datetime-local" value={time} onChange={e => setTime(e.target.value)} />
          <button onClick={book}>Book Appointment</button>

          <h3>Scheduled Appointments</h3>
          {appointments.length === 0 ? (
            <p className="muted">No appointments yet</p>
          ) : (
            <div>
              {appointments.map(a => (
                <div key={a.id} className="appointment-item">
                  <div><strong>{a.name}</strong></div>
                  <div className="appt-time">{a.time}</div>
                  <span className={`status-badge status-${a.status.replace('-', '')}`}>{a.status}</span>
                  <button className="btn-inline" onClick={() => startConsultation(a.id)} disabled={status === 'connecting'}>Start Consultation</button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="right-column">
          <h3>System Status</h3>
          <div className="status-box">
            <p>Current Status: <strong className="status-text">{status}</strong></p>
          </div>

          <h3>Reliability Controls</h3>
          <ul className="controls-list">
            <li>Simulated retry policy: exponential backoff</li>
            <li>Fallback to chat mode on video failure</li>
            <li>Humanization checklist gating</li>
          </ul>

          <HumanizationChecklist onComplete={setCanProceed} />
          <p className="muted" style={{ marginTop: 12 }}>Checklist complete: <strong>{canProceed ? '✓ Yes' : '✗ No'}</strong></p>
        </div>
      </div>

      {activeChat && (
        <ChatWindow
          appointmentName={appointments.find(a => a.id === activeChat)?.name || 'Patient'}
          onClose={() => setActiveChat(null)}
        />
      )}
    </div>
  );
}
