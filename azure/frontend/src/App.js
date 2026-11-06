import React, { useEffect, useState } from 'react';
import Map from "./Map";

function App() {
  // const [message, setMessage] = useState('');

  // useEffect(() => {
  //   fetch('/api/save-locations')
  //     .then((response) => response.json())
  //     .then((data) => setMessage(data.message))
  //     .catch((error) => console.error(error));
  // }, []);

  return (
    <div>
      <h1>!NotifyMe!</h1>
      <Map />
    </div>
  );
}

export default App;