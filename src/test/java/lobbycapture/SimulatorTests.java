package lobbycapture;


import java.io.IOException;


public final class SimulatorTests
{
	private SimulatorTests() {
	}
	
	static void main(String[] args) throws IOException {
		AdaptationTest.run();
		SmokeTest.run();
		System.out.println("All simulator tests passed.");
	}
}
