# Script to determine how to scale FT991 S-meter data

# From hamlib/newcat.c, for Yaesu FT991,
#     S0    =   0    = -54dB
#     S2    =  26
#     S4    =  51
#     S6    =  81
#     S7.5  = 105
#     S9    = 130
#     S9+12 = 157
#     S9+25 = 186
#     S9+35 = 203
#     S9+50 = 237
#     S9+60 = 255    = S0+114 dB
# So if we want to return 'S-units,' scale by 9/130 ?

x=[0,2,4,6,7.5,9,9+12/6,9+25/6,9+35/6,9+50/6,9+60/6]
y=[0,26,51,81,105,130,157,186,203,237,255]

plot(x,y,'b')
xlabel('S Units')
ylabel('Count')
hold on

p=polyfit(x,y,1)
p2=polyfit(y,x,1)

yy = polyval(p,x)

plot(x,yy,'r')

m=p2(1)
b=p2(2)
z=[0,255]
xx=m*z+b

plot(xx,z,'g-.')
