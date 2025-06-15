import usb.core
import usb.util
import time
from typing import Optional, Dict, List, Tuple, Any
import logging
import sys

class GoogleADKManager:
    """
    Google ADK Manager for implementing USB Host communication with Android devices.
    This class handles communication between Android devices and custom hardware accessories.
    """
    
    # Common Android device vendor IDs
    ANDROID_VENDOR_IDS = {
        0x18D1: "Google",  # Google
        0x22D9: "OPPO",    # OPPO
        0x2717: "Xiaomi",  # Xiaomi
        0x04E8: "Samsung", # Samsung
        0x0BB4: "HTC",     # HTC
        0x12D1: "Huawei",  # Huawei
    }
    
    # Android Accessory Protocol (ADK) Interface and Endpoint characteristics
    ADK_INTERFACE_CLASS = 0xFF  # Vendor Specific
    ADK_INTERFACE_SUBCLASS = 0xFF # Vendor Specific
    ADK_INTERFACE_PROTOCOL = 0x00 # Vendor Specific, though some devices might use 0x01 or 0x02

    def __init__(self):
        """Initialize the Google ADK Manager."""
        self.device = None
        self.connection = None
        self.interface = None
        self.endpoint_in = None
        self.endpoint_out = None
        self.setup_logging()
        self._check_usb_backend()
        self.operation_timeout = 5000  # 5 seconds timeout for USB operations (in milliseconds)

    def setup_logging(self):
        """Configure logging for the ADK manager."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('GoogleADKManager')

    def _check_usb_backend(self):
        """
        Check if a USB backend is available and provide helpful error messages.
        This function is crucial for ensuring libusb is correctly installed.
        """
        try:
            # Try to find any USB device to test backend presence
            test_dev = usb.core.find(find_all=True)
            if not list(test_dev): # Ensure the generator is consumed to trigger backend check
                self.logger.warning("No USB devices found by pyusb backend. This might be normal if no devices are connected.")
        except usb.core.NoBackendError:
            self.logger.error("No USB backend available. Please install libusb (e.g., via Zadig on Windows):")
            self.logger.error("1. Download Zadig from https://zadig.akeo.ie/")
            self.logger.error("2. Run Zadig and select 'libusb-win32' or 'WinUSB' as the driver for your Android device.")
            self.logger.error("3. Install the driver.")
            raise RuntimeError("No USB backend available. Please install libusb driver using Zadig.")

    def find_android_device(self) -> Optional[usb.core.Device]:
        """
        Find a connected Android device that matches the specified Vendor IDs.
        
        Returns:
            Optional[usb.core.Device]: The found Android device or None.
        """
        try:
            self.logger.info("Scanning for USB devices...")
            devices = usb.core.find(find_all=True)
            
            if not list(devices): # Consume generator to check if empty
                self.logger.warning("No USB devices found at all. Please check your USB connection.")
                self.logger.warning("\nPlease ensure:")
                self.logger.warning("1. Device is connected via USB.")
                self.logger.warning("2. USB debugging is enabled in Developer Options on your Android device.")
                self.logger.warning("3. USB configuration is set to 'File Transfer' or 'MTP' mode.")
                self.logger.warning("4. You have granted USB debugging permission on your device (look for a prompt).")
                return None
            
            found_devices_info = []
            for device in devices:
                vendor_id = device.idVendor
                product_id = device.idProduct
                vendor_name = self.ANDROID_VENDOR_IDS.get(vendor_id, "Unknown")
                
                device_info = f"Vendor: {vendor_name} (ID: {vendor_id:04x}), Product ID: {product_id:04x}"
                found_devices_info.append(device_info)
                self.logger.info(f"Found USB device: {device_info}")
                
                # Check if device is an Android device
                if vendor_id in self.ANDROID_VENDOR_IDS:
                    self.logger.info(f"Found Android device: {vendor_name}")
                    self.device = device # Store the device
                    return device
            
            if found_devices_info:
                self.logger.warning("Found USB devices, but none are recognized as Android devices (based on Vendor ID).")
                self.logger.warning("Detected devices:")
                for info in found_devices_info:
                    self.logger.warning(f"- {info}")
                self.logger.warning("\nPlease ensure your device's Vendor ID is in the supported list or add it.")
            else:
                self.logger.warning("No USB devices found. Is the device connected?")
            
            return None
            
        except usb.core.NoBackendError:
            # This case should ideally be caught by _check_usb_backend, but good to have here too.
            self.logger.error("USB backend disappeared or not available.")
            raise
        except Exception as e:
            self.logger.error(f"Error finding Android device: {str(e)}")
            return None

    def setup_usb_communication(self) -> bool:
        """
        Sets up the USB communication interface and endpoints for the ADK device.
        This should be called after a device has been found by find_android_device.
        
        Returns:
            bool: True if setup was successful, False otherwise.
        """
        if not self.device:
            self.logger.error("No Android device found to set up communication.")
            return False

        try:
            # Detach kernel driver if necessary (common on Linux)
            if sys.platform != "win32": # On Windows, libusb-win32/WinUSB usually handles this
                for cfg in self.device:
                    for intf in cfg:
                        if self.device.is_kernel_driver_active(intf.bInterfaceNumber):
                            try:
                                self.device.detach_kernel_driver(intf.bInterfaceNumber)
                                self.logger.info(f"Kernel driver detached from interface {intf.bInterfaceNumber}.")
                            except usb.core.USBError as e:
                                self.logger.warning(f"Could not detach kernel driver from interface {intf.bInterfaceNumber}: {e}")
                                continue

            # Set the configuration
            self.device.set_configuration()
            # Get a configuration instance for the device
            cfg = self.device.get_active_configuration()

            # Find the ADK interface and its endpoints
            for intf_obj in cfg:
                if (intf_obj.bInterfaceClass == self.ADK_INTERFACE_CLASS and
                    intf_obj.bInterfaceSubClass == self.ADK_INTERFACE_SUBCLASS and
                    intf_obj.bInterfaceProtocol == self.ADK_INTERFACE_PROTOCOL):
                    
                    self.interface = intf_obj
                    self.logger.info(f"Found ADK Interface: {intf_obj.bInterfaceNumber}")
                    
                    for ep in intf_obj:
                        if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                            self.endpoint_in = ep
                            self.logger.info(f"Found IN Endpoint: {ep.bEndpointAddress}")
                        else:
                            self.endpoint_out = ep
                            self.logger.info(f"Found OUT Endpoint: {ep.bEndpointAddress}")
                    break # Found the ADK interface, no need to check others

            if not self.interface or not self.endpoint_in or not self.endpoint_out:
                self.logger.error("Could not find ADK interface or required endpoints. Check device configuration.")
                self.logger.error("Expected Interface Class: 0xFF, SubClass: 0xFF, Protocol: 0x00")
                return False

            # Claim the interface
            self.connection = self.device.open()
            if self.connection:
                self.connection.claimInterface(self.interface)
                self.logger.info(f"Claimed interface {self.interface.bInterfaceNumber}.")
                return True
            else:
                self.logger.error("Failed to open USB device connection.")
                return False

        except usb.core.USBError as e:
            self.logger.error(f"USB error during setup: {e}")
            # If claiming fails, often means kernel driver is active or permission issue
            self.logger.error("Possible causes: device in use by another program, kernel driver active, or permission issue.")
            self.logger.error("On Linux, try: sudo rmmod cdc_acm; sudo rmmod usb_storage; then reconnect device.")
            self.logger.error("On Windows, ensure correct libusb/WinUSB driver is installed with Zadig and run as Administrator.")
            self.close() # Clean up any opened resources
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during USB setup: {e}")
            self.close() # Clean up any opened resources
            return False

    def send_data(self, data: bytes) -> bool:
        """
        Send data to the Android device via USB bulk transfer.
        
        Args:
            data: Data to send (bytes).
            
        Returns:
            bool: True if send was successful, False otherwise.
        """
        if not self.connection or not self.endpoint_out:
            self.logger.error("USB connection or OUT endpoint not ready for sending data.")
            return False
        
        try:
            self.logger.info(f"Sending {len(data)} bytes via USB: {data[:20]}...") # Log first 20 bytes
            bytes_sent = self.connection.bulkWrite(
                self.endpoint_out.bEndpointAddress,
                data,
                self.operation_timeout # Timeout in milliseconds
            )
            if bytes_sent == len(data):
                self.logger.info("Data sent successfully.")
                return True
            else:
                self.logger.warning(f"Sent {bytes_sent} bytes, expected {len(data)}.")
                return False
        except usb.core.USBError as e:
            self.logger.error(f"USB error during data send: {e}")
            if "timeout" in str(e).lower():
                self.logger.error("Send operation timed out. Device might not be responding.")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during data send: {e}")
            return False

    def receive_data(self, size: int = 64) -> Optional[bytes]:
        """
        Receive data from the Android device via USB bulk transfer.
        
        Args:
            size: Maximum number of bytes to read.
            
        Returns:
            Optional[bytes]: Received data as bytes, or None if an error or timeout occurs.
        """
        if not self.connection or not self.endpoint_in:
            self.logger.error("USB connection or IN endpoint not ready for receiving data.")
            return None

        try:
            self.logger.info(f"Waiting to receive up to {size} bytes via USB...")
            data = self.connection.bulkRead(
                self.endpoint_in.bEndpointAddress,
                size,
                self.operation_timeout # Timeout in milliseconds
            )
            if data and len(data) > 0:
                self.logger.info(f"Received {len(data)} bytes: {bytes(data)[:20]}...") # Log first 20 bytes
                return bytes(data)
            else:
                self.logger.warning("No data received (empty response or timeout).")
                return None
        except usb.core.USBError as e:
            self.logger.error(f"USB error during data receive: {e}")
            if "timeout" in str(e).lower():
                self.logger.warning("Receive operation timed out. No data from device.")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during data receive: {e}")
            return None

    def close(self):
        """
        Close all USB connections and release resources.
        """
        try:
            if self.connection and self.interface:
                self.connection.releaseInterface(self.interface)
                self.logger.info(f"Released interface {self.interface.bInterfaceNumber}.")
            if self.connection:
                self.connection.close()
                self.logger.info("Closed USB device connection.")
            if self.device:
                usb.util.dispose_resources(self.device)
                self.logger.info("Disposed USB device resources.")
            self.device = None
            self.connection = None
            self.interface = None
            self.endpoint_in = None
            self.endpoint_out = None
            self.logger.info("ADK Manager resources cleaned up.")
        except Exception as e:
            self.logger.error(f"Error during ADK Manager cleanup: {e}") 