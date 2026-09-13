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

	public static void main(String[] args) throws IOException {
		require(args.length == 1, "Supply the synthetic normalized procurement CSV");
		var records = CalibrationDataLoader.readProcurement(Path.of(args[0]));
		require(records.size() == 1, "Synthetic integration fixture has one row");
		require(!records.get(0).exclusionFlag(), "Normalization must not introduce vendor exclusion evidence");
		require(records.get(0).limitedCompetition(), "Competition procedure remains a separate proxy");
		System.out.println("Synthetic SAM normalization-to-Java exclusion check passed.");
	}
	
	public static void run() throws IOException {
		verifiesElectoralCommunicationFundingSources();
		verifiesProcurementExclusionEvidenceBoundary();
		System.out.println("Calibration loader tests passed.");
	}
	
	private static void verifiesElectoralCommunicationFundingSources() throws IOException {
		Path source = Files.createTempFile("fec-electoral-communication", ".csv");
		try {
			Files.writeString(
					source,
					"source,recipient,issueDomain,amount,flowType,traceability,largeDonorShare,disclosureLag\n"
							+ "Electioneering Filer,Candidate A,democracy,0.2500,ELECTIONEERING,0.5000,0.7400,0.2800\n"
							+ "Communication Spender,Candidate B,democracy,0.0100,COMMUNICATION_COST,0.6400,0.6600,0.1800\n"
			);
			List<FecRecord> records = CalibrationDataLoader.readFec(source);
			require(records.size() == 2, "FEC loader should read both electoral-communication rows");
			require(records.get(0).flowType() == FundingSource.ELECTIONEERING, "FEC loader should preserve electioneering rows");
			require(records.get(1).flowType() == FundingSource.COMMUNICATION_COST, "FEC loader should preserve communication-cost rows");
			require(records.get(0).disclosureLag() == 0.2800, "FEC loader should preserve disclosure lag rows");
		} finally {
			Files.deleteIfExists(source);
		}
	}
	
	private static void verifiesProcurementExclusionEvidenceBoundary() throws IOException {
		Path source = Files.createTempFile("synthetic-procurement-evidence", ".csv");
		String header = "awardId,recipient,issueDomain,amount,numberOfOffers,competitionType,exclusionFlag";
		String row = "SYNTHETIC-ORDER,SYNTHETIC VENDOR,procurement,1,4,FULL AND OPEN COMPETITION AFTER EXCLUSION OF SOURCES,false";
		try {
			Files.writeString(source, header + ",exclusionEvidenceStatus\n" + row + ",not_observed_in_contract_awards\n");
			var record = CalibrationDataLoader.readProcurement(source).get(0);
			require(!record.exclusionFlag(), "Unobserved SAM status must override the competition-text heuristic");
			require(record.limitedCompetition(), "The competition-procedure proxy remains separate");
			Files.writeString(source, header + "\n" + row + "\n");
			require(CalibrationDataLoader.readProcurement(source).get(0).exclusionFlag(), "Unmarked legacy fixtures retain proxy replay, not vendor-status evidence");
			Files.writeString(source, header + ",exclusionEvidenceStatus\n" + row + ",legacy_competition_proxy\n");
			require(CalibrationDataLoader.readProcurement(source).get(0).exclusionFlag(), "Explicit legacy proxy keeps its declared meaning");
			for (String status : List.of("", "unknown", "observed_vendor_exclusion")) {
				Files.writeString(source, header + ",exclusionEvidenceStatus\n" + row + "," + status + "\n");
				try {
					CalibrationDataLoader.readProcurement(source);
					throw new AssertionError("Unsupported exclusion evidence status must fail closed");
				} catch (IllegalArgumentException expected) {
					require(expected.getMessage().contains("exclusion evidence status"), "Reject unsupported evidence metadata");
				}
			}
			Files.writeString(source, header + ",exclusionEvidenceStatus\n" + row.replace(",false", ",true") + ",not_observed_in_contract_awards\n");
			try {
				CalibrationDataLoader.readProcurement(source);
				throw new AssertionError("A true flag must not contradict unobserved status");
			} catch (IllegalArgumentException expected) {
				require(expected.getMessage().contains("exclusion flag contradicts"), "Reject contradictory evidence metadata");
			}
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
