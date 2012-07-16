counter|100
rec|def() {
   print(counter " ")
   if >(counter|-(counter 1) 0) {
      rec()
   }
}
main|def() {
   println("Counting down from" counter)
   rec()
   println()
}
