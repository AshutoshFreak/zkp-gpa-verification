# Handling Decimal Values in Zero-Knowledge Proofs

## The Challenge with Decimal Values

Zero-Knowledge Proof systems like circom work with finite fields and can only process integer values. However, many real-world values such as GPAs (e.g., 3.8) are decimal values. This document explains how our system handles decimal values in ZKP circuits.

## Our Approach: Scaling

To handle decimal values, we use a scaling approach:

1. **Scale Up**: Before sending values to the ZKP circuit, we multiply them by a scaling factor to convert them to integers. 
   - For example, with a scaling factor of 100, a GPA of 3.8 becomes 380.

2. **Scale in Circuit**: The ZKP circuit operates on these scaled integer values.
   - For example, comparing if 380 >= 350 (for a threshold of 3.5).

3. **Scale Down**: When displaying results, we divide by the scaling factor to return to the original decimal scale.

## Advantages of Scaling

- **Precision**: Allows us to maintain precision for decimal values.
- **Simplicity**: The ZKP circuit still works with integers only, which is what it's designed for.
- **Flexibility**: The scaling factor can be adjusted based on the required precision.

## Implementation Details

In our system:

1. The `CredentialHolder` class handles scaling up when generating proofs:
   ```python
   # Scale values to integers for ZKP circuit
   score_int = int(score_value * scale_factor)
   threshold_int = int(threshold * scale_factor)
   ```

2. The scaling factor is included in the proof metadata:
   ```python
   proof_data["metadata"] = {
       # ...other metadata...
       "scale_factor": scale_factor
   }
   ```

3. The `ProofVerifier` class is aware of the scaling when interpreting results.

## Default Scaling Factor

Our system uses a default scaling factor of 100, which allows for two decimal places of precision. This is sufficient for GPAs (typically expressed with one decimal place) and most other academic scores.

## Limitations

- **Fixed Precision**: The scaling approach has fixed precision.
- **Range Limitations**: Very large values might exceed the range of the finite field.
- **Rounding Errors**: Converting to integers may introduce small rounding errors.

For most academic applications, these limitations are not significant concerns.
