#include <stdio.h>
#include <stdint.h>
#include "firmware/model/model_weights.h"  // contains everything: constants, struct, prototypes

int main(void) {
    HybridModelBuffers buffers;
    model_init(&buffers);

    int8_t input[INPUT_SIZE];
    for (int i = 0; i < INPUT_SIZE; i++) {
        input[i] = (int8_t)((i * 37) % 256 - 128);
    }

    model_predict(&buffers, input, 0);

    printf("LOGITS");
    for (int i = 0; i < OUTPUT_SIZE; i++) {
        printf(" %d", buffers.output[i]);
    }
    printf("\n");

    return 0;
}
