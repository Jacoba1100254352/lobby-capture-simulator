package lobbycapture;


import java.io.IOException;


public final class SimulatorTests
{
	private SimulatorTests() {
	}
	
	public static void main(String[] args) throws IOException {
		AdaptationTest.run();
		SmokeTest.run();
		System.out.println("All simulator tests passed.");
	}
}
