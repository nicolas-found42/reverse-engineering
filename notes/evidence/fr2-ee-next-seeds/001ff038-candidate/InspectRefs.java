//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.util.*;

/** Read-only: dump reference types/sources and flow info; never starts a transaction. */
public class InspectRefs extends GhidraScript {
    public void run() throws Exception {
        AddressSpace sp = currentProgram.getAddressFactory().getDefaultAddressSpace();
        Function f = currentProgram.getFunctionManager().getFunctionAt(sp.getAddress(0x00200d10L));
        println("INSPECT function=" + f.getName() + " source=" + f.getSymbol().getSource() + " body=" + f.getBody().getNumAddresses());
        Map<String,Integer> hist = new TreeMap<>();
        int shown = 0;
        for (Instruction i : currentProgram.getListing().getInstructions(f.getBody(), true)) {
            for (Reference r : i.getReferencesFrom()) {
                String key = r.getReferenceType() + "|" + r.getSource() + "|" + (r.isMemoryReference() ? "mem" : "other");
                hist.merge(key, 1, Integer::sum);
                if (r.getReferenceType().isFlow() && shown < 14) { println("REF " + i.getAddress() + " -> " + r.getToAddress() + " " + key + " flowtype=" + i.getFlowType() + " fall=" + i.getFallThrough()); shown++; }
            }
        }
        println("HIST " + hist);
        Address entry = sp.getAddress(0x001ff038L);
        for (Reference r : currentProgram.getReferenceManager().getReferencesTo(entry)) println("TO001ff038 " + r.getFromAddress() + " " + r.getReferenceType() + " " + r.getSource());
        println("FUNC at 001ff038: " + currentProgram.getFunctionManager().getFunctionAt(entry) + " count=" + currentProgram.getFunctionManager().getFunctionCount());
    }
}
