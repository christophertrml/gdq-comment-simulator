package analyzer

object SpeedrunCollector {
    case class Prize(
        prizeId: Int,
        name: String,
        contributedBy: Option[String],
        entryThreshold: Double,
        startGameId: Int,
        endGameId: Int,
        category: Option[String],
        imageLink: Option[String])

    
}