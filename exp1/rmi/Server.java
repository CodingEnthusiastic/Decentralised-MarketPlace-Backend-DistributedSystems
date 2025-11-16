import java.rmi.*;
import java.rmi.registry.*;
import java.rmi.server.*;

// -------- Remote Interface --------
interface Calculator extends Remote {
    int add(int a, int b) throws RemoteException;
    int multiply(int a, int b) throws RemoteException;
}

// -------- Implementation --------
class CalculatorImpl extends UnicastRemoteObject implements Calculator {

    protected CalculatorImpl() throws RemoteException {
        super();
    }

    public int add(int a, int b) throws RemoteException {
        return a + b;
    }

    public int multiply(int a, int b) throws RemoteException {
        return a * b;
    }
}

// -------- Server Main --------
public class Server {
    public static void main(String[] args) {
        try {
            CalculatorImpl obj = new CalculatorImpl();

            // Create Registry at port 1099
            Registry reg = LocateRegistry.createRegistry(1099);

            // Bind the service
            reg.rebind("CalcService", obj);

            System.out.println("RMI Calculator Server running on port 1099...");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
