package lobbycapture.simulation;


import java.util.Random;


public record RandomSource(Random random)
{
	public RandomSource(long random) {
		this(new Random(random));
	}
}

