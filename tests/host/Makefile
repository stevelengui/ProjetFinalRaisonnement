CC = gcc
CFLAGS = -O2 -Wall -I. -Ifirmware/model -Iops -Iutils \
         -DINPUT_SIZE=360 -DCONV1_FILTERS=6 -DCONV2_FILTERS=12 \
         -DLSTM_HIDDEN=24 -DSNN_HIDDEN=24 -DOUTPUT_SIZE=5 \
         -DTIME_STEPS=32 -DQ_BITS=8 -DFIXED_SCALE=8

SRCS = main_host.c \
       firmware/model/model.c \
       firmware/model/model_weights.c \
       ops/math_ops.c \
       cycle_count_host.c

all: main_host

main_host: $(SRCS)
	$(CC) $(CFLAGS) $(SRCS) -o main_host

clean:
	rm -f main_host
