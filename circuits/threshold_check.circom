pragma circom 2.0.0;

// Import comparators from circomlib
include "../node_modules/circomlib/circuits/comparators.circom";

/*
 * ThresholdCheck circuit
 * 
 * This circuit verifies if a student's score meets or exceeds a threshold
 * without revealing the actual score.
 *
 * Inputs:
 *   - score: The student's score (private input)
 *   - threshold: The required threshold (public input)
 *
 * Output:
 *   - out: 1 if score >= threshold, 0 otherwise
 */
template ThresholdCheck() {
    signal input score;
    signal input threshold;
    signal output out;
    
    // Calculate the difference between score and threshold
    signal diff <== score - threshold;
    
    // Use GreaterEqThan component from circomlib to check if diff >= 0
    // Note: We need to specify a range for the inputs
    // For academic scores, 100 bits should be more than enough
    component isGteZero = GreaterEqThan(100);
    isGteZero.in[0] <== diff;
    isGteZero.in[1] <== 0;
    
    // Output the result
    out <== isGteZero.out;
}

component main = ThresholdCheck();
