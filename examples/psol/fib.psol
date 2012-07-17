fib:def() {
   a:0 b:1
   def() {
      b:+(a a:b)
      a
   }
}

fib_printer:def(i f) {
   if >(i 0) {
         println(f())
         fib_printer(-(i 1) f)
   }
}

main:def() {
   f:fib() i:20
   println("Printing" i "Fibonacci numbers:")
   fib_printer(i f)
   0
}
