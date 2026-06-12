package lobbycapture;


import lobbycapture.budget.FundingSource;
import lobbycapture.calibration.CalibrationDataLoader;
import lobbycapture.calibration.FecRecord;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;


public final class CalibrationLoaderTest
{
	private CalibrationLoaderTest() {
	}
	
	public static void run() throws IOException {
		verifiesElectoralCommunicationFundingSources();
		System.out.println("Calibration loader tests passed.");
	}
	
	private static void verifiesElectoralCommunicationFundingSources() throws IOException {
		Path source = Files.createTempFile("fec-electoral-communication", ".csv");
		try {
			Files.writeString(
					source,
					"source,recipient,issueDomain,amount,flowType,traceability,largeDonorShare\n"
							+ "Electioneering Filer,Candidate A,democracy,0.2500,ELECTIONEERING,0.5000,0.7400\n"
							+ "Communication Spender,Candidate B,democracy,0.0100,COMMUNICATION_COST,0.6400,0.6600\n"
			);
			List<FecRecord> records = CalibrationDataLoader.readFec(source);
			require(records.size() == 2, "FEC loader should read both electoral-communication rows");
			require(records.get(0).flowType() == FundingSource.ELECTIONEERING, "FEC loader should preserve electioneering rows");
			require(records.get(1).flowType() == FundingSource.COMMUNICATION_COST, "FEC loader should preserve communication-cost rows");
		} finally {
			Files.deleteIfExists(source);
		}
	}
	
	private static void require(boolean condition, String message) {
		if (!condition) {
			throw new AssertionError(message);
		}
	}
}
