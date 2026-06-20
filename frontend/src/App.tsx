import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import CommandCenter from './pages/CommandCenter';
import Dashboard from './pages/Dashboard';
import Briefings from './pages/Briefings';
import Decisions from './pages/Decisions';
import Intent from './pages/Intent';
import Relationships from './pages/Relationships';
import Memory from './pages/Memory';
import Trust from './pages/Trust';
import Founder from './pages/Founder';
import IngestionCenter from './pages/IngestionCenter';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<CommandCenter />} />
          <Route path="overview" element={<Dashboard />} />
          <Route path="ingestion" element={<IngestionCenter />} />
          <Route path="briefings" element={<Briefings />} />
          <Route path="decisions" element={<Decisions />} />
          <Route path="intent" element={<Intent />} />
          <Route path="relationships" element={<Relationships />} />
          <Route path="memory" element={<Memory />} />
          <Route path="trust" element={<Trust />} />
          <Route path="founder" element={<Founder />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
