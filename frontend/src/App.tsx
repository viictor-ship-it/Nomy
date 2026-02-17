import { useState } from "react";
import { Toaster } from "react-hot-toast";
import { RoomView } from "./components/RoomView";

const DEFAULT_ROOM = "example-room";

export default function App() {
  const [roomId] = useState(DEFAULT_ROOM);

  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: "#1f2937", color: "#f9fafb", border: "1px solid #374151" },
        }}
      />
      <RoomView roomId={roomId} />
    </>
  );
}
