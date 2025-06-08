#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <algorithm>

struct IdVolume {
    int64_t id;
    int64_t volume;
};

struct PriceVolume {
    double price;
    int64_t volume;
};

/*
 * Complete the member functions below as per the question's description.
 */
 

class TestSolution {
  public:
    
    TestSolution(const std::vector<std::string>& data);
    
    std::unordered_map<std::string, int64_t> OrderCounts();
    std::vector<IdVolume> BiggestBuyOrders(const std::string& symbol);
    PriceVolume BestSellAtTime(const std::string& symbol, const std::string& timestamp);

  private:
    std::vector<std::string> data_;
};

int main()
{
    std::vector<std::string> data;
    std::string line;
    while (std::getline(std::cin, line)) {
        data.emplace_back(line);
    }
    
    TestSolution solution{data};

    const std::unordered_map<std::string, int64_t> orderCounts = solution.OrderCounts();
    std::vector<std::pair<std::string, int64_t>> sortedOrderCounts(orderCounts.begin(), orderCounts.end());
    std::sort(sortedOrderCounts.begin(), sortedOrderCounts.end(), [](const auto& l, const auto& r) {
        return l.first < r.first;
    });
    std::cout << "Order counts:\n";
    for (const auto& [symbol, count] : sortedOrderCounts) {
        std::cout << symbol << " " << count << "\n";
    }
    
    std::vector<IdVolume> biggestBuyOrders = solution.BiggestBuyOrders("DVAM1");
    std::sort(biggestBuyOrders.begin(), biggestBuyOrders.end(), [](const auto& l, const auto& r) {
        return (l.volume > r.volume) || (l.volume == r.volume && l.id < r.id);
    });
    std::cout << "\nBiggest buys:\n";
    for (const IdVolume& idVolume : biggestBuyOrders) {
        std::cout << idVolume.id << " " << idVolume.volume << "\n";
    }
    
    const PriceVolume priceVolume = solution.BestSellAtTime("DVAM1", "15:30:00");
    std::cout << "\nBest sell:\n";
    std::cout << priceVolume.price << " " << priceVolume.volume << "\n";

    return 0;
} 