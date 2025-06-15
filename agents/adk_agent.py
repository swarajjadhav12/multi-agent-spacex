import logging
from core.google_adk_manager import GoogleADKManager
import time

class ADKAgent:
    """Agent for handling Google ADK (Accessory Development Kit) operations."""
    
    # Class-level variable to maintain connection state
    _instance = None
    _is_connected = False
    
    def __new__(cls):
        """Ensure only one instance of ADKAgent exists."""
        if cls._instance is None:
            cls._instance = super(ADKAgent, cls).__new__(cls)
            cls._instance.adk_manager = GoogleADKManager()
            cls._instance.device = None
            cls._instance.setup_logging()
        return cls._instance
    
    def setup_logging(self):
        """Configure logging for the ADK agent."""
        self.logger = logging.getLogger('ADKAgent')
        
    def connect_device(self) -> bool:
        """
        Connect to the Android device.
        
        Returns:
            bool: True if connection was successful
        """
        try:
            if self._is_connected:
                self.logger.info("Already connected to device")
                return True
                
            self.device = self.adk_manager.find_android_device()
            if not self.device:
                self.logger.error("No Android device found")
                return False
                
            # Now, set up USB communication instead of serial communication
            if self.adk_manager.setup_usb_communication():
                self.logger.info("Successfully connected to device via USB")
                self._is_connected = True
                return True
            else:
                self.logger.error("Failed to set up USB communication")
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to device: {str(e)}")
            return False
            
    def run(self, input_data=None) -> dict:
        """
        Run the ADK agent.
        
        Args:
            input_data: Optional input data for the agent
            
        Returns:
            dict: Result of the operation
        """
        try:
            # If no input data, try to connect to device
            if input_data is None:
                if self.connect_device():
                    return {"status": "success", "message": "Connected to device"}
                else:
                    return {"status": "error", "message": "Failed to connect to device"}
                    
            # Process input data
            if isinstance(input_data, dict):
                action = input_data.get("action")
                
                if not self._is_connected and action != "close":
                    self.logger.error("Not connected to device")
                    return {"status": "error", "message": "Not connected to device"}
                
                if action == "send":
                    data = input_data.get("data")
                    if not data:
                        return {"status": "error", "message": "No data provided to send"}
                        
                    self.logger.info(f"Attempting to send data: {data}")
                    if self.adk_manager.send_data(data.encode()):
                        # Wait a short time for the device to process
                        time.sleep(0.5)
                        
                        # Try to receive response
                        self.logger.info("Waiting for response...")
                        response = self.adk_manager.receive_data()
                        if response:
                            return {
                                "status": "success", 
                                "message": "Data sent and response received",
                                "sent_data": data,
                                "received_data": response.decode()
                            }
                        else:
                            return {
                                "status": "warning",
                                "message": "Data sent but no response received",
                                "sent_data": data
                            }
                    else:
                        return {"status": "error", "message": "Failed to send data"}
                        
                elif action == "receive":
                    self.logger.info("Attempting to receive data...")
                    data = self.adk_manager.receive_data()
                    if data:
                        return {
                            "status": "success", 
                            "message": "Data received successfully",
                            "data": data.decode()
                        }
                    else:
                        return {
                            "status": "warning",
                            "message": "No data received within timeout period"
                        }
                        
                elif action == "close":
                    self.adk_manager.close()
                    self._is_connected = False
                    return {"status": "success", "message": "Connection closed"}
                    
            return {"status": "error", "message": "Unknown action"}
            
        except Exception as e:
            self.logger.error(f"Error in ADK agent run: {str(e)}")
            return {"status": "error", "message": str(e)} 